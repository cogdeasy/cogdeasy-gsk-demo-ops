from __future__ import annotations

import httpx
import pytest

from demo_ops.http import HttpClient, HttpError


def client(handler: object, calls: list[httpx.Request], attempts: int = 4) -> HttpClient:
    def record(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return handler(request)  # type: ignore[operator, no-any-return]

    return HttpClient(
        transport=httpx.MockTransport(record), attempts=attempts, sleep=lambda _: None
    )


def test_posts_json_and_returns_object() -> None:
    calls: list[httpx.Request] = []
    http = client(lambda r: httpx.Response(201, json={"key": "GSK-9"}), calls)
    status, body = http.post_json("https://x.test/p", {"a": 1}, {"H": "v"})
    assert (status, body) == (201, {"key": "GSK-9"})
    assert calls[0].headers["H"] == "v"
    assert calls[0].headers["Content-Type"] == "application/json"
    assert calls[0].content == b'{"a":1}'


def test_non_json_body_returns_empty_dict() -> None:
    http = client(lambda r: httpx.Response(200, text="ok"), [])
    assert http.post_json("https://hooks.test/x", {}) == (200, {})


@pytest.mark.parametrize("status", [429, 503])
def test_retries_statuses_where_nothing_was_created(status: int) -> None:
    calls: list[httpx.Request] = []
    responses = iter([httpx.Response(status), httpx.Response(status), httpx.Response(201)])
    http = client(lambda r: next(responses), calls)
    assert http.post_json("https://x.test/p", {})[0] == 201
    assert len(calls) == 3


def test_gives_up_after_attempts() -> None:
    calls: list[httpx.Request] = []
    http = client(lambda r: httpx.Response(503), calls, attempts=3)
    with pytest.raises(HttpError, match=r"HTTP 503 from x\.test"):
        http.post_json("https://x.test/p", {})
    assert len(calls) == 3


def test_does_not_retry_other_errors_and_hides_url_path() -> None:
    calls: list[httpx.Request] = []
    http = client(lambda r: httpx.Response(400, json={"errorMessages": ["bad field"]}), calls)
    with pytest.raises(HttpError) as err:
        http.post_json("https://hooks.test/services/T0/B0/SECRET", {})
    assert len(calls) == 1
    assert err.value.status == 400
    assert "bad field" in str(err.value)
    assert "SECRET" not in str(err.value)


def test_retries_connect_errors_only() -> None:
    calls: list[httpx.Request] = []
    attempts = iter([httpx.ConnectError("down"), None])

    def handler(request: httpx.Request) -> httpx.Response:
        exc = next(attempts)
        if exc:
            raise exc
        return httpx.Response(200, json={"ok": True})

    assert client(handler, calls).post_json("https://x.test/p", {})[1] == {"ok": True}
    assert len(calls) == 2


def test_read_timeout_is_not_retried() -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow")

    with pytest.raises(HttpError, match="ReadTimeout"):
        client(handler, calls).post_json("https://x.test/p", {})
    assert len(calls) == 1
