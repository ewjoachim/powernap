from __future__ import annotations

from typing import NoReturn

import httpx
from typing_extensions import TypeAlias

METHODS = {"get", "put", "post", "patch", "delete"}


class PowerNapError(Exception):
    pass


ResponseType: TypeAlias = "JsonObject | str | bytes"


class PowerNap:
    """Simplistic REST API Client"""

    def __init__(self, httpx_client: httpx.Client):
        """
        Simplistic REST API Client

        Parameters
        ----------
        httpx_client : httpx.Client
            You probably want the client to have some attributes set:

            - `base_url` to indicate the url where your API is located
            - `headers` for authentication
        """
        self.httpx_client = httpx_client

    def __call__(self, *attr: str):
        return PathAttribute(client=self, path="")(*attr)

    def __getattr__(self, attr: str):
        return PathAttribute(client=self, path=f"/{attr}")

    def handle_exception(self, exc: httpx.HTTPError) -> NoReturn:
        """
        Override this method to handle exception.
        This lets you choose what type of exception may then bubble up in your
        code.

        Parameters
        ----------
        exc : httpx.HTTPError
            The httpx error received when calling the API

        Returns
        -------
        NoReturn
            This method should never return. Returning from this method is
            an error.

        Raises
        ------
        exc
            You can raise anything here.
        """
        raise exc

    def http(self, method: str, path: str, **kwargs) -> httpx.Response:
        method = method.lower()

        try:
            response: httpx.Response = getattr(self.httpx_client, method)(
                path,
                **kwargs,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            self.handle_exception(exc)
            raise PowerNapError("handle_exception should always raise")

        return response


def response_contents(response: httpx.Response) -> ResponseType:
    content_type = response.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        return response.json(object_hook=JsonObject)

    elif content_type.startswith("text/"):
        return response.text

    return response.content


class JsonObject(dict):
    """
    general json object that can bind any fields but also act as a dict.
    """

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(rf"'Dict' object has no attribute '{key}'")


class MethodCaller:
    def __init__(self, client: PowerNap, method: str, arg: str, path: str):
        self.client = client
        self.method = method
        self.arg = arg
        self.path = path

    def __call__(self, **kwargs) -> ResponseType:
        return response_contents(self.io(**{self.arg: kwargs}))

    def i(self, **kwargs) -> ResponseType:
        return response_contents(self.io(**kwargs))

    def o(self, **kwargs) -> httpx.Response:
        return self.io(**{self.arg: kwargs})

    def io(self, **kwargs) -> httpx.Response:
        return self.client.http(method=self.method, path=self.path, **kwargs)


class PathAttribute:
    def __init__(self, client, path):
        self.client = client
        self.path = path

    def __call__(self, *args):
        if not args:
            return self
        path = "/".join(str(arg) for arg in [self.path, *args] if arg)
        return PathAttribute(client=self.client, path=path)

    def __getattr__(self, attr):
        path = f"{self.path}/{attr}"
        return PathAttribute(client=self.client, path=path)

    # We could generate all those in a loop but we'd loose typing.

    @property
    def get(self) -> MethodCaller:
        return MethodCaller(
            client=self.client, method="get", arg="params", path=self.path
        )

    @property
    def put(self) -> MethodCaller:
        return MethodCaller(
            client=self.client, method="put", arg="json", path=self.path
        )

    @property
    def post(self) -> MethodCaller:
        return MethodCaller(
            client=self.client, method="post", arg="json", path=self.path
        )

    @property
    def patch(self) -> MethodCaller:
        return MethodCaller(
            client=self.client, method="patch", arg="json", path=self.path
        )

    @property
    def delete(self) -> MethodCaller:
        return MethodCaller(
            client=self.client, method="delete", arg="params", path=self.path
        )
