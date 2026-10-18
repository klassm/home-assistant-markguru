from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from .const import API_LIMIT, API_URL, DEFAULT_API_KEY, DEFAULT_CLIENT_KEY
from .models import Offer

logger = logging.getLogger(__name__)


class MarktguruApiError(Exception):
    """Raised when the Marktguru API request fails."""


class MarktguruClient:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        client_key: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self._session = session
        self._headers = {
            "x-clientkey": client_key or DEFAULT_CLIENT_KEY,
            "x-apikey": api_key or DEFAULT_API_KEY,
        }

    async def search_offers(
        self,
        query: str,
        zip_code: str,
    ) -> list[Offer]:
        params: dict[str, Any] = {
            "as": "web",
            "limit": API_LIMIT,
            "offset": 0,
            "q": query,
            "zipCode": zip_code,
        }
        try:
            async with asyncio.timeout(10):
                resp = await self._session.get(
                    API_URL,
                    params=params,
                    headers=self._headers,
                )
                resp.raise_for_status()
                data = await resp.json()
        except TimeoutError as err:
            raise MarktguruApiError(
                f"Timeout fetching offers for query '{query}'"
            ) from err
        except aiohttp.ClientError as err:
            raise MarktguruApiError(
                f"Error fetching offers for query '{query}': {err}"
            ) from err

        results = data.get("results", [])
        return [Offer.from_api(r) for r in results]

    async def test_connection(self, zip_code: str) -> bool:
        params: dict[str, Any] = {
            "as": "web",
            "limit": 1,
            "offset": 0,
            "q": "test",
            "zipCode": zip_code,
        }
        try:
            async with asyncio.timeout(10):
                resp = await self._session.get(
                    API_URL,
                    params=params,
                    headers=self._headers,
                )
                resp.raise_for_status()
                return True
        except (TimeoutError, aiohttp.ClientError):
            return False
