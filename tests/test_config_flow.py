from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.marktguru.const import (
    CONF_ALLOWED_RETAILERS,
    CONF_API_KEY,
    CONF_CLIENT_KEY,
    CONF_PRODUCTS,
    CONF_SCAN_INTERVAL,
    CONF_ZIP_CODE,
    DEFAULT_ALLOWED_RETAILERS,
    DEFAULT_SCAN_INTERVAL,
)


class TestConfigFlowStepUser:
    @pytest.mark.asyncio
    async def test_user_step_shows_form(self):
        from custom_components.marktguru.config_flow import MarktguruConfigFlow

        flow = MarktguruConfigFlow()
        flow.hass = MagicMock()

        with patch(
            "custom_components.marktguru.config_flow.async_get_clientsession",
            return_value=MagicMock(),
        ):
            result = await flow.async_step_user(None)

        assert result["step_id"] == "user"
        assert "data_schema" in result

    @pytest.mark.asyncio
    async def test_user_step_connection_fails(self):
        from custom_components.marktguru.api_client import MarktguruClient
        from custom_components.marktguru.config_flow import MarktguruConfigFlow

        flow = MarktguruConfigFlow()
        flow.hass = MagicMock()

        mock_client = AsyncMock(spec=MarktguruClient)
        mock_client.test_connection.return_value = False

        with (
            patch(
                "custom_components.marktguru.config_flow.MarktguruClient",
                return_value=mock_client,
            ),
            patch(
                "custom_components.marktguru.config_flow.async_get_clientsession",
                return_value=MagicMock(),
            ),
        ):
            result = await flow.async_step_user(
                {
                    CONF_ZIP_CODE: "86156",
                    CONF_CLIENT_KEY: "test-key",
                    CONF_API_KEY: "test-api",
                }
            )

        assert result["errors"]["base"] == "cannot_connect"

    @pytest.mark.asyncio
    async def test_user_step_connection_success_proceeds(self):
        from custom_components.marktguru.api_client import MarktguruClient
        from custom_components.marktguru.config_flow import MarktguruConfigFlow

        flow = MarktguruConfigFlow()
        flow.hass = MagicMock()

        mock_client = AsyncMock(spec=MarktguruClient)
        mock_client.test_connection.return_value = True

        with (
            patch(
                "custom_components.marktguru.config_flow.MarktguruClient",
                return_value=mock_client,
            ),
            patch(
                "custom_components.marktguru.config_flow.async_get_clientsession",
                return_value=MagicMock(),
            ),
        ):
            result = await flow.async_step_user(
                {
                    CONF_ZIP_CODE: "86156",
                    CONF_CLIENT_KEY: "test-key",
                    CONF_API_KEY: "test-api",
                }
            )

        assert result["step_id"] == "products"


class TestConfigFlowStepProducts:
    @pytest.mark.asyncio
    async def test_products_step_empty_products(self):
        from custom_components.marktguru.config_flow import MarktguruConfigFlow

        flow = MarktguruConfigFlow()
        flow._client_key = "test-key"
        flow._api_key = "test-api"
        flow._zip_code = "86156"
        flow.hass = MagicMock()

        result = await flow.async_step_products(
            {
                CONF_PRODUCTS: "",
                CONF_ALLOWED_RETAILERS: DEFAULT_ALLOWED_RETAILERS,
            }
        )

        assert result["errors"]["base"] == "products_required"

    @pytest.mark.asyncio
    async def test_products_step_success(self):
        from custom_components.marktguru.config_flow import MarktguruConfigFlow

        flow = MarktguruConfigFlow()
        flow._client_key = "test-key"
        flow._api_key = "test-api"
        flow._zip_code = "86156"
        flow.hass = MagicMock()

        result = await flow.async_step_products(
            {
                CONF_PRODUCTS: "Franziskaner, Paulaner",
                CONF_ALLOWED_RETAILERS: DEFAULT_ALLOWED_RETAILERS,
            }
        )

        assert result["type"] == "create_entry"
        assert result["title"] == "Marktguru (86156)"
        assert result["data"][CONF_PRODUCTS] == ["Franziskaner", "Paulaner"]
        assert result["data"][CONF_ZIP_CODE] == "86156"
        assert result["data"][CONF_CLIENT_KEY] == "test-key"
        assert result["data"][CONF_API_KEY] == "test-api"

    @pytest.mark.asyncio
    async def test_products_step_strips_whitespace(self):
        from custom_components.marktguru.config_flow import MarktguruConfigFlow

        flow = MarktguruConfigFlow()
        flow._client_key = "test-key"
        flow._api_key = "test-api"
        flow._zip_code = "86156"
        flow.hass = MagicMock()

        result = await flow.async_step_products(
            {
                CONF_PRODUCTS: "  Franziskaner ,  Paulaner  ",
                CONF_ALLOWED_RETAILERS: DEFAULT_ALLOWED_RETAILERS,
            }
        )

        assert result["data"][CONF_PRODUCTS] == ["Franziskaner", "Paulaner"]


class TestOptionsFlow:
    @pytest.mark.asyncio
    async def test_options_flow_init(self):
        from custom_components.marktguru.config_flow import MarktguruOptionsFlow

        config_entry = MagicMock()
        config_entry.data = {
            CONF_ZIP_CODE: "86156",
            CONF_CLIENT_KEY: "test-key",
            CONF_API_KEY: "test-api",
            CONF_PRODUCTS: ["Franziskaner"],
            CONF_ALLOWED_RETAILERS: DEFAULT_ALLOWED_RETAILERS,
            CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
        }
        config_entry.options = {}

        flow = MarktguruOptionsFlow(config_entry)
        flow.hass = MagicMock()

        result = await flow.async_step_init(None)

        assert result["step_id"] == "init"

    @pytest.mark.asyncio
    async def test_options_flow_save(self):
        from custom_components.marktguru.config_flow import MarktguruOptionsFlow

        config_entry = MagicMock()
        config_entry.data = {
            CONF_ZIP_CODE: "86156",
            CONF_CLIENT_KEY: "test-key",
            CONF_API_KEY: "test-api",
            CONF_PRODUCTS: ["Franziskaner"],
            CONF_ALLOWED_RETAILERS: DEFAULT_ALLOWED_RETAILERS,
            CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
        }
        config_entry.options = {}

        flow = MarktguruOptionsFlow(config_entry)
        flow.hass = MagicMock()

        result = await flow.async_step_init(
            {
                CONF_PRODUCTS: "Franziskaner, Paulaner",
                CONF_ALLOWED_RETAILERS: ["REWE", "Kaufland"],
                CONF_SCAN_INTERVAL: 6,
            }
        )

        assert result["type"] == "create_entry"
        assert result["data"][CONF_PRODUCTS] == ["Franziskaner", "Paulaner"]
        assert result["data"][CONF_ALLOWED_RETAILERS] == ["REWE", "Kaufland"]
        assert result["data"][CONF_SCAN_INTERVAL] == 6

    @pytest.mark.asyncio
    async def test_options_flow_empty_products(self):
        from custom_components.marktguru.config_flow import MarktguruOptionsFlow

        config_entry = MagicMock()
        config_entry.data = {
            CONF_PRODUCTS: ["Franziskaner"],
            CONF_ALLOWED_RETAILERS: DEFAULT_ALLOWED_RETAILERS,
            CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
        }
        config_entry.options = {}

        flow = MarktguruOptionsFlow(config_entry)
        flow.hass = MagicMock()

        result = await flow.async_step_init(
            {
                CONF_PRODUCTS: "",
                CONF_ALLOWED_RETAILERS: DEFAULT_ALLOWED_RETAILERS,
                CONF_SCAN_INTERVAL: 12,
            }
        )

        assert result["errors"]["base"] == "products_required"
