from __future__ import annotations

import httpx
import pytest

import powernap


@pytest.fixture
def httpx_client(checker):
    class HttpClient(checker.Checker):
        def response(self, **kwargs):
            kwargs.setdefault("status_code", 200)
            request_kwargs = self.match.match_kwargs.copy()
            request_kwargs.pop("timeout", None)
            request_kwargs["method"] = self.match.method
            return httpx.Response(
                request=httpx.Request(**request_kwargs),
                **kwargs,
            )

    return checker(
        HttpClient(
            call=httpx.Client,
        )
    )


@pytest.fixture
def api_client(httpx_client):
    return powernap.PowerNap(httpx_client=httpx_client)


def test_client__get(httpx_client, api_client: powernap.PowerNap):
    httpx_client.register.get("/repos/a/b/issues", params={"a": 1})(json={"foo": "bar"})

    response = api_client.repos("a/b").issues.get(a=1)

    assert isinstance(response, powernap.JsonObject)  # Ok, that's just for mypy
    assert response == {"foo": "bar"}
    assert response.foo == "bar"


def test_client__get__root(httpx_client, api_client: powernap.PowerNap):
    httpx_client.register.get("a/b")()

    api_client("a/b").get(a=1)


def test_client__get__empty_root(httpx_client, api_client: powernap.PowerNap):
    httpx_client.register.get("")()

    api_client().get()


def test_client__get__text(httpx_client, api_client: powernap.PowerNap):
    httpx_client.register.get("/repos/a/b/issues", params={"a": 1})(
        content="foo", headers={"Content-Type": "text/plain"}
    )

    response = api_client.repos("a/b").issues.get(a=1)

    assert response == "foo"


def test_client__get__bytes(httpx_client, api_client: powernap.PowerNap):
    httpx_client.register.get("/repos/a/b/issues", params={"a": 1})(
        content=b"foo", headers={"Content-Type": "application/octet-stream"}
    )

    response = api_client.repos("a/b").issues.get(a=1)

    assert response == b"foo"


def test_client__get__output(httpx_client, api_client: powernap.PowerNap):
    httpx_client.register.get("/repos/a/b/issues", params={"a": 1})(json={"foo": "bar"})

    response = api_client.repos("a/b").issues.get.o(a=1)

    assert isinstance(response, httpx.Response)


def test_client__get__input(httpx_client, api_client: powernap.PowerNap):
    httpx_client.register.get("/repos/a/b/issues", params={"a": 1})(json={"foo": "bar"})

    response = api_client.repos("a/b").issues.get.i(params={"a": 1})

    assert response.foo == "bar"


def test_client__get__input_output(httpx_client, api_client: powernap.PowerNap):
    httpx_client.register.get("/repos/a/b/issues", params={"a": 1})(json={"foo": "bar"})

    response = api_client.repos("a/b").issues.get.io(params={"a": 1})

    assert isinstance(response, httpx.Response)


def test_client__post(httpx_client, api_client: powernap.PowerNap):
    httpx_client.register.post("/repos/a/b/issues", json={"a": 1})(text="foo")

    assert api_client.repos("a/b").issues.post(a=1) == "foo"


def test_client__put(httpx_client, api_client: powernap.PowerNap):
    httpx_client.register.put("/repos/a/b/issues", json={"a": 1})(text="foo")

    assert api_client.repos("a/b").issues.put(a=1) == "foo"


def test_client__patch(httpx_client, api_client: powernap.PowerNap):
    httpx_client.register.patch("/repos/a/b/issues", json={"a": 1})(text="foo")

    assert api_client.repos("a/b").issues.patch(a=1) == "foo"


def test_client__delete(httpx_client, api_client: powernap.PowerNap):
    httpx_client.register.delete("/repos/a/b/issues", params={"a": 1})(text="foo")

    assert api_client.repos("a/b").issues.delete(a=1) == "foo"


def test_json_object():
    obj = powernap.JsonObject({"a": 1})

    assert obj.a == 1


def test_json_object__error():
    obj = powernap.JsonObject({"a": 1})

    with pytest.raises(AttributeError):
        obj.b


def test_client__get_error(httpx_client, api_client: powernap.PowerNap):
    httpx_client.register.get("/repos")(status_code=404)

    with pytest.raises(httpx.HTTPStatusError):
        api_client.repos.get()


def test_handle_exceptions_not_handled(httpx_client):
    class MyPowerNap(powernap.PowerNap):
        def handle_exception(self, exc: httpx.HTTPError):
            pass

    httpx_client.register.get("")(status_code=404)

    with pytest.raises(powernap.PowerNapError):
        MyPowerNap(httpx_client=httpx_client)().get()
