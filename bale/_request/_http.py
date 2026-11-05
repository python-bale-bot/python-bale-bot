# An API wrapper for Bale written in Python
# Copyright (c) 2022-2026
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from __future__ import annotations

import asyncio
import inspect
import logging
from collections.abc import Callable, Coroutine
from typing import Any, cast

import aiohttp

from .._exceptions import (BadRequest, BaleError, Forbidden, InvalidToken,
                           NetworkError, NotFound, RateLimited, TimeOut)
from .._utils import request as utils_request
from ..constants import BALE_API_BASE_URL, BALE_API_FILE_URL
from ._parser import BaleResponse

__all__ = ("HTTPClient", "Route")

_log = logging.getLogger(__name__)


class Route:
    """
    Arguments:
        request_method:
            The HTTP method to be used (e.g., ``GET``, ``POST``, ``PUT`` & ``DELETE``).
        endpoint:
            The endpoint URL of the request.
        token:
            Bot’s unique authentication token.
        base_url:
            Bot API service URL.

            .. tip::

                To automatically place the token in the initial URL, replace the string ``TOKEN`` with your token.

                For example: ``https://tapi.bale.ai/bot{TOKEN}``

    """

    __slots__ = ("base_url", "request_method", "endpoint", "token")

    def __init__(
        self,
        request_method: str,
        endpoint: str,
        token: str,
        base_url: str = BALE_API_BASE_URL,
    ) -> None:
        if not isinstance(request_method, str):
            raise TypeError("request_method param must be str.")
        if not isinstance(endpoint, str):
            raise TypeError("endpoint param must be str.")
        if not isinstance(token, str):
            raise TypeError("token param must be str.")
        if not isinstance(base_url, str):
            raise TypeError("base_url param must be str.")

        self.base_url = base_url
        self.request_method = request_method
        self.endpoint = endpoint
        self.token = token

    @property
    def url(self) -> str:
        """The final URL based on the given information.

        The following strings are concatenated in order and returned:

        - The initial request URL, which, if it contains the term ``"TOKEN"``, is replaced by the given token.
        - The request endpoint.
        """
        return self.base_url.format(TOKEN=self.token) + self.endpoint

    @property
    def masked_url(self) -> str:
        return self.url.replace(self.token, "****", 1)


class HTTPClient:
    """Send a Request to BALE API Server"""

    __slots__ = (
        "token",
        "session",
        "connector_init",
        "http_trace",
        "proxy",
        "proxy_auth",
    )

    def __init__(
        self,
        token: str,
        connector_init: dict[str, Any] | None = None,
        http_trace: aiohttp.TraceConfig | None = None,
        proxy: str | None = None,
        proxy_auth: aiohttp.BasicAuth | None = None,
    ) -> None:
        if not isinstance(token, str):
            raise TypeError("token param must be type of str.")

        if not connector_init:
            connector_init = {
                "keepalive_timeout": 20.0,
                "ttl_dns_cache": 300,
                "enable_cleanup_closed": True,
            }

        self.session: aiohttp.ClientSession | None = None
        self.token = token
        self.connector_init = connector_init
        self.http_trace = http_trace
        self.proxy = proxy
        self.proxy_auth = proxy_auth

    @property
    def user_agent(self) -> str:
        return "python-bale-bot (https://python-bale-bot.ir): An API wrapper for Bale written in Python"

    def get_session(self) -> aiohttp.ClientSession:
        if not self.session:
            raise TypeError(
                "session is not initialized. Please call `.start()` before using this method."
            )
        return self.session

    def is_closed(self) -> bool:
        return self.session is None

    def create_session(self) -> None:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(**self.connector_init),
                headers={
                    "User-Agent": self.user_agent,
                },
                trace_configs=[self.http_trace] if self.http_trace else None,
            )

    async def start(self) -> None:
        if self.session:
            raise RuntimeError("HTTPClient has already started.")

        self.create_session()

    async def close(self) -> None:
        if self.session is not None and not self.session.closed:
            await self.session.close()
            # Wait 250ms = 0.250s for the underlying SSL connections to close
            # https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
            await asyncio.sleep(0.250)

        self.session = None

    def validate_response(self, response: "BaleResponse") -> None:
        """Checks the response from the `Bale <https://ble.ir>`_ Bot API and raises appropriate exceptions if needed.

        This function validates the HTTP response status and raises corresponding exceptions
        based on the error type returned by the `Bale <https://ble.ir>`_ API.

        The function handles the following response status codes:

        - ``200``-``299``: Success, no exception is raised.
        - ``404``: Raises :exc:`~bale.NotFound`.
        - ``403``: Raises :exc:`~bale.Forbidden`.
        - ``400``: Raises :exc:`~bale.BadRequest`.
        - ``429``: Raises :exc:`~bale.RateLimited` with retry delay if provided.
        - ``502``: Raises :exc:`~bale.NetworkError`.
        - Any other status code results in a generic :exc:`~bale.BaleError`.

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                response = BaleResponse(...)
                check_response(response)  # Raises an exception if the response indicates an error

        Arguments:
            response:
                The parsed API response to be checked.

        Raises
        ------
        bale.NotFound
            If the requested resource is not found.
        bale.Forbidden
            If the bot lacks necessary permissions.
        bale.BadRequest
            If the request parameters are incorrect.
        bale.RateLimited
            If the bot has exceeded the rate limit.
        bale.NetworkError
            If there is a server-side issue.
        bale.BaleError
            If an unknown error occurs.


        .. versionadded:: 3.0

        """
        original_response = response.original_response
        status_code = original_response.status

        if response.ok and 200 <= status_code < 300:
            return

        parameters = response.parameters
        ResponseStatusCode = utils_request.ResponseStatusCode

        message = response.description or "Unknown error"
        if (
            status_code == ResponseStatusCode.UNAUTHORIZED
            or InvalidToken.check_description(message)
        ):
            raise InvalidToken(message)
        if status_code == ResponseStatusCode.NOT_FOUND:
            raise NotFound(message)
        if status_code == ResponseStatusCode.FORBIDDEN:
            raise Forbidden(message)
        if status_code == ResponseStatusCode.BAD_REQUEST:
            raise BadRequest(message)
        if status_code == ResponseStatusCode.RATE_LIMIT:
            retry_after = parameters.retry_after if parameters else None
            raise RateLimited(retry_after)
        if status_code == ResponseStatusCode.BAD_GATEWAY:
            raise NetworkError(message)

        raise BaleError(f"{message}: {status_code}")

    async def request(
        self, route: Route, *, form_data: aiohttp.FormData | None = None, **kwargs
    ) -> BaleResponse:
        url, masked_url = route.url, route.masked_url
        method = route.request_method
        headers = {}

        if "json" in kwargs:
            headers["Content-Type"] = "application/json"
            kwargs["data"] = utils_request.to_json(kwargs.pop("json"))
        if form_data:
            kwargs["data"] = form_data

        if self.proxy is not None:
            kwargs["proxy"] = self.proxy
        if self.proxy_auth is not None:
            kwargs["proxy_auth"] = self.proxy_auth

        kwargs["headers"] = headers

        try:
            async with self.get_session().request(
                method=method, url=url, **kwargs  # noqa
            ) as original_response:
                _log.debug(
                    "[%s] %s with %s has returned %s",
                    method,
                    masked_url,
                    kwargs.get("data"),
                    original_response.status,
                )
                response = await BaleResponse.from_response(original_response)
                self.validate_response(response)

                return cast(BaleResponse, response)
        except aiohttp.ServerTimeoutError as exc:
            raise TimeOut() from exc
        except asyncio.TimeoutError as exc:
            raise TimeOut() from exc
        except aiohttp.ClientError as exc:
            raise NetworkError(f"{exc.__class__.__name__}: {exc}") from exc

    async def get_file(self, file_id: str):
        base_file_url = BALE_API_FILE_URL.format(TOKEN=self.token)

        try:
            async with self.get_session().get(
                f"{base_file_url}/{file_id}", raise_for_status=True
            ) as original_response:
                return await original_response.read()
        except aiohttp.ServerTimeoutError as exc:
            raise TimeOut() from exc
        except aiohttp.ClientError as exc:
            raise NetworkError(f"{exc.__class__.__name__}: {exc}") from exc

    async def download_file(
        self,
        file_id: str,
        write_func: Callable[[Any], Any],
        *,
        chunk_size: int = 64 << 10,
        progress: (
            Callable[[int | None, float], Coroutine[Any, Any, Any] | Any] | None
        ) = None,
        **kwargs,
    ) -> None:
        base_file_url = BALE_API_FILE_URL.format(TOKEN=self.token)
        is_awaitable = inspect.isawaitable(progress) if progress is not None else False

        try:
            async with self.get_session().get(
                f"{base_file_url}/{file_id}", raise_for_status=True, **kwargs  # noqa
            ) as response:
                total = response.headers.get("Content-Length")
                total = int(total) if str(total).isdigit() else None
                downloaded = 0.0

                async for chunk in response.content.iter_chunked(chunk_size):
                    downloaded += len(chunk)
                    write_func(chunk)
                    if progress:
                        coro = progress(total, downloaded)
                        if is_awaitable:
                            await coro
        except aiohttp.ServerTimeoutError as exc:
            raise TimeOut() from exc
        except aiohttp.ClientError as exc:
            raise NetworkError(f"{exc.__class__.__name__}: {exc}") from exc
