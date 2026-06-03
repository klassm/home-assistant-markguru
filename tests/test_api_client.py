from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from custom_components.marktguru.api_client import MarktguruClient


def _make_response(
    status: int = 200, json_data: dict | None = None, raise_error: bool = False
):
    resp = AsyncMock()
    resp.status = status
    resp.raise_for_status = MagicMock()
    if raise_error:
        resp.raise_for_status.side_effect = aiohttp.ClientResponseError(
            request_info=MagicMock(), history=()
        )
    if json_data is not None:
        resp.json = AsyncMock(return_value=json_data)
    return resp


class TestSearchOffers:
    @pytest.mark.asyncio
    async def test_success(self, sample_api_response):
        session = AsyncMock(spec=aiohttp.ClientSession)
        resp = _make_response(json_data=sample_api_response)
        session.get = AsyncMock(return_value=resp)

        client = MarktguruClient(
            session=session,
            client_key="test-client-key",
            api_key="test-api-key",
        )
        offers = await client.search_offers("Franziskaner", "86156")
        assert len(offers) == 2
        assert offers[0].price == 9.99
        assert offers[1].price == 12.99

    @pytest.mark.asyncio
    async def test_empty_results(self):
        session = AsyncMock(spec=aiohttp.ClientSession)
        resp = _make_response(json_data={"results": []})
        session.get = AsyncMock(return_value=resp)

        client = MarktguruClient(
            session=session,
            client_key="test-client-key",
            api_key="test-api-key",
        )
        offers = await client.search_offers("NonExistent", "86156")
        assert len(offers) == 0

    @pytest.mark.asyncio
    async def test_http_error(self):
        session = AsyncMock(spec=aiohttp.ClientSession)
        resp = _make_response(status=500, raise_error=True)
        session.get = AsyncMock(return_value=resp)

        client = MarktguruClient(
            session=session,
            client_key="test-client-key",
            api_key="test-api-key",
        )
        offers = await client.search_offers("Franziskaner", "86156")
        assert len(offers) == 0

    @pytest.mark.asyncio
    async def test_timeout(self):
        session = AsyncMock(spec=aiohttp.ClientSession)
        session.get = AsyncMock(side_effect=TimeoutError())

        client = MarktguruClient(
            session=session,
            client_key="test-client-key",
            api_key="test-api-key",
        )
        offers = await client.search_offers("Franziskaner", "86156")
        assert len(offers) == 0

    @pytest.mark.asyncio
    async def test_connection_error(self):
        session = AsyncMock(spec=aiohttp.ClientSession)
        session.get = AsyncMock(side_effect=aiohttp.ClientError())

        client = MarktguruClient(
            session=session,
            client_key="test-client-key",
            api_key="test-api-key",
        )
        offers = await client.search_offers("Franziskaner", "86156")
        assert len(offers) == 0

    @pytest.mark.asyncio
    async def test_headers_sent(self, sample_api_response):
        session = AsyncMock(spec=aiohttp.ClientSession)
        resp = _make_response(json_data=sample_api_response)
        session.get = AsyncMock(return_value=resp)

        client = MarktguruClient(
            session=session,
            client_key="test-client-key",
            api_key="test-api-key",
        )
        await client.search_offers("Franziskaner", "86156")

        call_kwargs = session.get.call_args
        assert call_kwargs.kwargs["headers"]["x-clientkey"] == "test-client-key"
        assert call_kwargs.kwargs["headers"]["x-apikey"] == "test-api-key"

    @pytest.mark.asyncio
    async def test_query_params(self, sample_api_response):
        session = AsyncMock(spec=aiohttp.ClientSession)
        resp = _make_response(json_data=sample_api_response)
        session.get = AsyncMock(return_value=resp)

        client = MarktguruClient(
            session=session,
            client_key="test-client-key",
            api_key="test-api-key",
        )
        await client.search_offers("Paulaner", "10115")

        call_kwargs = session.get.call_args
        params = call_kwargs.kwargs["params"]
        assert params["q"] == "Paulaner"
        assert params["zipCode"] == "10115"
        assert params["as"] == "web"
        assert params["limit"] == 24


class TestTestConnection:
    @pytest.mark.asyncio
    async def test_success(self):
        session = AsyncMock(spec=aiohttp.ClientSession)
        resp = _make_response(json_data={"results": []})
        session.get = AsyncMock(return_value=resp)

        client = MarktguruClient(
            session=session,
            client_key="test-client-key",
            api_key="test-api-key",
        )
        result = await client.test_connection("86156")
        assert result is True

    @pytest.mark.asyncio
    async def test_failure(self):
        session = AsyncMock(spec=aiohttp.ClientSession)
        resp = _make_response(status=403, raise_error=True)
        session.get = AsyncMock(return_value=resp)

        client = MarktguruClient(
            session=session,
            client_key="test-client-key",
            api_key="test-api-key",
        )
        result = await client.test_connection("86156")
        assert result is False

    @pytest.mark.asyncio
    async def test_timeout(self):
        session = AsyncMock(spec=aiohttp.ClientSession)
        session.get = AsyncMock(side_effect=TimeoutError())

        client = MarktguruClient(
            session=session,
            client_key="test-client-key",
            api_key="test-api-key",
        )
        result = await client.test_connection("86156")
        assert result is False
