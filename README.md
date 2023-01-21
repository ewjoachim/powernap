# PowerNap

[![Deployed to PyPI](https://img.shields.io/pypi/pyversions/powernap?logo=pypi&logoColor=white)](https://pypi.org/pypi/powernap)
[![GitHub Repository](https://img.shields.io/github/stars/ewjoachim/powernap?logo=github)](https://github.com/ewjoachim/powernap/)
[![Continuous Integration](https://img.shields.io/github/actions/workflow/status/ewjoachim/powernap/ci.yml?logo=github)](https://github.com/ewjoachim/powernap/actions?workflow=CI)
[![Coverage](https://raw.githubusercontent.com/ewjoachim/powernap/python-coverage-comment-action-data/badge.svg)](https://github.com/ewjoachim/powernap/tree/python-coverage-comment-action-data)
[![MIT License](https://img.shields.io/github/license/ewjoachim/powernap?logo=open-source-initiative&logoColor=white)](https://github.com/ewjoachim/powernap/blob/main/LICENSE.md)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v1.4%20adopted-ff69b4.svg)](https://github.com/ewjoachim/powernap/blob/main/LICENSE/CODE_OF_CONDUCT.md)

_A small REST client that recharges your batteries_

PowerNap is a simplistic JSON REST API client, a small wrapper around httpx that makes your code
read slightly better.

## Installation

```console
$ pip install powernap
```

## Usage

```python
# You will need an httpx Client. Let's do a GitHub client!
httpx_client = httpx.Client(
    base_url="https://api.github.com/v3",
    headers={"Authorization": f"token {token}"}
)

# Instantiate the PowerNap client
github_client = powernap.PowerNap(httpx_client=httpx_client)

# PowerNap will help you build complex URLs in a pythonic-looking way:
repo = github_client.repos("ewjoachim/powernap").get()

# And access the json responses like objects
count_stars = repo.stargazers_count

# You can also easily send POST requests.
github_client.repos("ewjoachim/powernap").issues(42).comments.post(
    body=f"Wow look! This repo has {count_stars} stars!"
)
```

### Build complex URLs

You can use `client(something)` or `client.something`, and chain calls.
With the form `client(something)`, you can pass multiple parameters, and they
will be joined together

```python

# The next calls are all identical and target:
#    {base_url}/repos/ewjoachim/powernap/stargazers
github_client.repos("ewjoachim/powernap").stargazers.get()
github_client.repos("ewjoachim").powernap("stargazers").get()
github_client.repos("ewjoachim", "powernap", "stargazers").get()
github_client.repos("ewjoachim", "powernap")("stargazers").get()
github_client("repos/ewjoachim/powernap/stargazers").get()

# The recommended way is to use client.something for static parts of the url and
# client(something) with a variable for dynamic parts.

# You can also target the base url directly
# {base_url}
github_client().get()
```

### Access the json responses like objects

On the json responses, all objects (even nested) are configured so that you can
get keys with the `object.key` syntax in addition to the classic
`object["key"]`.

```python
# GET /nested_json -> {"a": {"b":{"c": "d"}}}
response = some_api_client.nested_json.get()

assert response == {"a": {"b":{"c": "d"}}}
assert response["a"]["b"]["c"] == "d"
# But also the magic form:
assert response.a.b.c == "d"
```

### Arguments

The arguments in the `.get/delete()` calls are used as query parameters on
the call.

The arguments in the `.post/put/patch()` calls are put together, and passed
as the json payload for the call.


### Response types

If the response comes with `Content-Type: application/json`, then you'll get
the "magic" json response as described above. Otherwise, if the content type
is `text/*`, you'll get a `string`, and otherwise, you'll get `bytes`.

### Exceptions

If you want to avoid `httpx` exceptions to reach your code, so as to maintain
a good abstraction layer, you may want to subclass Powernap and implement
`handle_exception(self, exc)`. You'll receive an `httpx.HttpError` and it's
your responsibility to raise whatever exception you see fit. Not raising an
exception in this context is considered as an error, though.

```python
from typing import NoReturn

class ApiError(MyProjectError):
    pass

class ForbiddenError(ApiError):
    pass

class ApiClient(PowerNap):
    def handle_exception(self, exc: httpx.HttpError) -> NoReturn:
        if exc.response.status_code == 403:
            raise ForbiddenError
        raise ApiError
```

### More control over input and output

This magic is nice and all, but sometimes, you may want more control.
If you want to send additional headers or a non-JSON-dict payload, or
if you want to read the headers on the response, it possible too.

Instead of calling `.get()`, use either `.get.i()`, `.get.o()` or `.get.io()`
(it works with any method: `get/post/put/patch/delete`):

- If you call with `.get.i(...)` (or `.get.io(...)`), you control the input.
  The method keyword arguments will be passed to the underlying
  `httpx.Client().get(...)` as-is.
- If you call with `.get.o(...)` (or `.get.io(...)`), you get the original
  output. The function will return a `httpx.Response` object. (Note that in
  this case, we will still have called `.raise_for_status()`)

If you regularly use `get.io()`, it's probably that PowerNap is probably not
the project you need. Use `httpx.Client` directly, build something to help you
craft URLs (you can ~~steal~~ copy the relevant code, don't forget to copy the
license too)

## Name

While looking for a name for this lib, I looked at all the synonyms for "small
rest". It's amazing how many other projects have gone the same route. To name a
few:
- [`nap`](https://pypi.org/project/nap/) looks awesome! Unrelated lib but same
  goals as this one. Seems unmaintained but I'm not sure a lib like this needs
  a lot of maintenance.
- [`catnap`](https://pypi.org/project/Catnap/)
- [`respite`](https://pypi.org/project/respite/)
- `snooze` is not taken but
  [`snooze-server`](https://pypi.org/project/snooze-server/) is and I didn't
  want to create confusion.

Funnily enough, a consequent number of those projects have the same goals as
this one, yet don't have the exact look and feel I'm trying to achieve.

## Credits where due

This lib is heavily inspired from githubpy, which is under Apache license.

- [The version that was used for inspiration](https://github.com/michaelliao/githubpy/blob/96d0c3e729c0b3e3c043a604547ccff17782ac2b/github.py)
- Author: Michael Liao (askxuefeng@gmail.com)
- [Original license](https://github.com/michaelliao/githubpy/blob/96d0c3e729c0b3e3c043a604547ccff17782ac2b/LICENSE.txt)
