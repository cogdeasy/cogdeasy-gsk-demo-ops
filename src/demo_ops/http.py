"""The one HTTP layer every API caller in this repo goes through.

httpx and tenacity are imported when a client is built, so --dry-run paths run on a bare
python3 without the package dependencies installed.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any
from urllib.parse import urlsplit

if TYPE_CHECKING:
    import httpx

DEFAULT_TIMEOUT = 15.0
DEFAULT_ATTEMPTS = 4
# Only 429 (rate limited: the request was refused, not processed), so a retried POST cannot
# create a second Jira issue or Devin session. A 503 or read timeout may follow a completed
# write, so neither is retried.
RETRY_STATUSES = frozenset({429})


class HttpError(RuntimeError):
    def __init__(self, status: int, host: str, detail: str = "") -> None:
        self.status = status
        self.host = host
        super().__init__(f"HTTP {status} from {host}" + (f": {detail}" if detail else ""))


class _RetryableStatus(Exception):
    def __init__(self, status: int) -> None:
        self.status = status


def _host(url: str) -> str:
    # Webhook URLs carry their secret in the path; never echo more than the host.
    return urlsplit(url).netloc or "<invalid url>"


class HttpClient:
    def __init__(
        self,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        attempts: int = DEFAULT_ATTEMPTS,
        transport: httpx.BaseTransport | None = None,
        sleep: Callable[[float], None] | None = None,
    ) -> None:
        import httpx

        self._httpx = httpx
        self._client = httpx.Client(timeout=timeout, transport=transport)
        self._attempts = attempts
        self._sleep = sleep

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _retryable(self, exc: BaseException) -> bool:
        return isinstance(
            exc, _RetryableStatus | self._httpx.ConnectError | self._httpx.ConnectTimeout
        )

    def post_json(
        self, url: str, body: Mapping[str, Any], headers: Mapping[str, str] | None = None
    ) -> tuple[int, dict[str, Any]]:
        """POST a JSON body; return (status, JSON object body or {})."""
        from tenacity import Retrying, retry_if_exception, stop_after_attempt, wait_exponential

        retrying = Retrying(
            retry=retry_if_exception(self._retryable),
            stop=stop_after_attempt(self._attempts),
            wait=wait_exponential(multiplier=0.5, max=8),
            reraise=True,
            sleep=self._sleep or time.sleep,
        )
        try:
            response = retrying(self._post_once, url, body, headers or {})
        except _RetryableStatus as exc:
            raise HttpError(exc.status, _host(url), "gave up after retries") from None
        except self._httpx.HTTPError as exc:
            raise HttpError(0, _host(url), type(exc).__name__) from None
        if not response.is_success:
            # Redirects are not followed (httpx default), so a 3xx means nothing was delivered.
            detail = _redact(_error_detail(response), url, headers or {})
            raise HttpError(response.status_code, _host(url), detail)
        return response.status_code, _json_object(response.content)

    def _post_once(
        self, url: str, body: Mapping[str, Any], headers: Mapping[str, str]
    ) -> httpx.Response:
        response = self._client.post(
            url, json=body, headers={"Accept": "application/json", **headers}
        )
        if response.status_code in RETRY_STATUSES:
            raise _RetryableStatus(response.status_code)
        return response


def _json_object(content: bytes) -> dict[str, Any]:
    if not content.strip().startswith(b"{"):
        return {}
    parsed = json.loads(content)
    return parsed if isinstance(parsed, dict) else {}


def _error_detail(response: httpx.Response) -> str:
    try:
        payload = _json_object(response.content)
    except ValueError:
        return ""
    messages = payload.get("errorMessages") or payload.get("errors") or payload.get("detail")
    return json.dumps(messages)[:300] if messages else ""


def _redact(text: str, url: str, headers: Mapping[str, str]) -> str:
    """Strip the URL path, query and header values (tokens, webhook secrets) from text."""
    parts = urlsplit(url)
    secrets = {url, parts.path, parts.query, *parts.path.split("/")}
    for value in headers.values():
        secrets.update({value, *value.split()})
    for secret in sorted((s for s in secrets if len(s) >= 6), key=len, reverse=True):
        text = text.replace(secret, "<redacted>")
    return text
