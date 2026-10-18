from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
)

from .api_client import MarktguruClient
from .const import (
    CONF_ALLOWED_RETAILERS,
    CONF_API_KEY,
    CONF_CLIENT_KEY,
    CONF_PRODUCTS,
    CONF_SCAN_INTERVAL,
    CONF_ZIP_CODE,
    DEFAULT_ALLOWED_RETAILERS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    KNOWN_RETAILERS,
)

logger = logging.getLogger(__name__)


class MarktguruConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._client_key: str = ""
        self._api_key: str = ""
        self._zip_code: str = ""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            self._client_key = user_input.get(CONF_CLIENT_KEY, "")
            self._api_key = user_input.get(CONF_API_KEY, "")
            self._zip_code = user_input[CONF_ZIP_CODE]

            session = async_get_clientsession(self.hass)
            client = MarktguruClient(
                session=session,
                client_key=self._client_key,
                api_key=self._api_key,
            )

            if await client.test_connection(self._zip_code):
                return await self.async_step_products()
            errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ZIP_CODE): TextSelector(
                        TextSelectorConfig(type="text")
                    ),
                    vol.Optional(CONF_CLIENT_KEY): TextSelector(
                        TextSelectorConfig(type="text")
                    ),
                    vol.Optional(CONF_API_KEY): TextSelector(
                        TextSelectorConfig(type="text")
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_products(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            products = [
                p.strip() for p in user_input.get(CONF_PRODUCTS, []) if p.strip()
            ]

            allowed_retailers = user_input.get(
                CONF_ALLOWED_RETAILERS, DEFAULT_ALLOWED_RETAILERS
            )

            if not products:
                errors["base"] = "products_required"
            else:
                return self.async_create_entry(
                    title=f"Marktguru ({self._zip_code})",
                    data={
                        CONF_ZIP_CODE: self._zip_code,
                        CONF_CLIENT_KEY: self._client_key,
                        CONF_API_KEY: self._api_key,
                        CONF_PRODUCTS: products,
                        CONF_ALLOWED_RETAILERS: allowed_retailers,
                        CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
                    },
                )

        return self.async_show_form(
            step_id="products",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PRODUCTS): SelectSelector(
                        SelectSelectorConfig(
                            multiple=True,
                            custom_value=True,
                        )
                    ),
                    vol.Required(
                        CONF_ALLOWED_RETAILERS, default=DEFAULT_ALLOWED_RETAILERS
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=KNOWN_RETAILERS,
                            multiple=True,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> MarktguruOptionsFlow:
        return MarktguruOptionsFlow(config_entry)


class MarktguruOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            products = [
                p.strip() for p in user_input.get(CONF_PRODUCTS, []) if p.strip()
            ]

            allowed_retailers = user_input.get(
                CONF_ALLOWED_RETAILERS,
                self._config_entry.data.get(
                    CONF_ALLOWED_RETAILERS, DEFAULT_ALLOWED_RETAILERS
                ),
            )
            scan_interval = user_input.get(
                CONF_SCAN_INTERVAL,
                self._config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            )

            if not products:
                errors["base"] = "products_required"
            else:
                return self.async_create_entry(
                    data={
                        CONF_PRODUCTS: products,
                        CONF_ALLOWED_RETAILERS: allowed_retailers,
                        CONF_SCAN_INTERVAL: int(scan_interval),
                    }
                )

        current_products = self._config_entry.options.get(
            CONF_PRODUCTS,
            self._config_entry.data.get(CONF_PRODUCTS, []),
        )
        current_retailers = self._config_entry.options.get(
            CONF_ALLOWED_RETAILERS,
            self._config_entry.data.get(
                CONF_ALLOWED_RETAILERS, DEFAULT_ALLOWED_RETAILERS
            ),
        )
        current_scan = self._config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self._config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PRODUCTS, default=current_products): (
                        SelectSelector(
                            SelectSelectorConfig(
                                multiple=True,
                                custom_value=True,
                            )
                        )
                    ),
                    vol.Required(
                        CONF_ALLOWED_RETAILERS, default=current_retailers
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=KNOWN_RETAILERS,
                            multiple=True,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=int(current_scan)
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=1,
                            max=24,
                            mode=NumberSelectorMode.SLIDER,
                        )
                    ),
                }
            ),
            errors=errors,
        )
