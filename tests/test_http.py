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


def test_retries_rate_limit() -> None:
    status = 429
    calls: list[httpx.Request] = []
    responses = iter([httpx.Response(status), httpx.Response(status), httpx.Response(201)])
    http = client(lambda r: next(responses), calls)
    assert http.post_json("https://x.test/p", {})[0] == 201
    assert len(calls) == 3


def test_gives_up_after_attempts() -> None:
    calls: list[httpx.Request] = []
    http = client(lambda r: httpx.Response(429), calls, attempts=3)
    with pytest.raises(HttpError, match=r"HTTP 429 from x\.test"):
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


@pytest.mark.parametrize("status", [500, 502, 503])
def test_server_errors_are_not_retried(status: int) -> None:
    calls: list[httpx.Request] = []
    http = client(lambda r: httpx.Response(status), calls)
    with pytest.raises(HttpError):
        http.post_json("https://x.test/p", {})
    assert len(calls) == 1


def test_redirect_is_not_reported_as_delivered() -> None:
    calls: list[httpx.Request] = []
    redirect = httpx.Response(302, headers={"Location": "https://elsewhere.test/"})
    http = client(lambda r: redirect, calls)
    with pytest.raises(HttpError) as err:
        http.post_json("https://hooks.test/x", {})
    assert err.value.status == 302
    assert len(calls) == 1


def test_error_detail_redacts_url_and_header_secrets() -> None:
    body = {"errorMessages": ["bad hook https://hooks.test/T0/B0/SECRETPATH token tok-SECRETVAL"]}
    http = client(lambda r: httpx.Response(400, json=body), [])
    with pytest.raises(HttpError) as err:
        http.post_json("https://hooks.test/T0/B0/SECRETPATH", {}, {"X-Secret": "tok-SECRETVAL"})
    message = str(err.value)
    assert "bad hook" in message
    assert "SECRETPATH" not in message
    assert "SECRETVAL" not in message


def test_error_detail_redacts_query_tokens_and_encoded_paths() -> None:
    body = {"detail": "token qtok1234 rejected for hooks.test%2FT0%2FB0%2FSECRETPATH"}
    http = client(lambda r: httpx.Response(401, json=body), [])
    with pytest.raises(HttpError) as err:
        http.post_json("https://hooks.test/T0/B0/SECRETPATH?token=qtok1234", {})
    message = str(err.value)
    assert "rejected" in message
    assert "qtok1234" not in message
    assert "SECRETPATH" not in message
