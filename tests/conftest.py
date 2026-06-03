from __future__ import annotations

import sys
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

import pytest


class _MockCoordinatorEntity:
    def __init__(self, coordinator: Any) -> None:
        self.coordinator = coordinator

    def __class_getitem__(cls, item: Any) -> type:
        return cls


class _MockSensorEntity:
    def __init_subclass__(cls, **kwargs: Any) -> None:
        pass

    def __init__(self, **kwargs: Any) -> None:
        pass

    @property
    def unique_id(self) -> str | None:
        return getattr(self, "_attr_unique_id", None)

    @property
    def name(self) -> str | None:
        return getattr(self, "_attr_name", None)

    @property
    def native_unit_of_measurement(self) -> str | None:
        return getattr(self, "_attr_native_unit_of_measurement", None)

    @property
    def device_class(self) -> Any:
        return getattr(self, "_attr_device_class", None)


class _MockDataUpdateCoordinator:
    def __init__(self, hass: Any, logger: Any, name: str = "", **kwargs: Any) -> None:
        self.hass = hass
        self.logger = logger
        self.name = name
        self.data: Any = None

    def __class_getitem__(cls, item: Any) -> type:
        return cls


class _MockConfigFlow:
    VERSION = 1

    def __init_subclass__(cls, domain: str = "", **kwargs: Any) -> None:
        pass

    def __init__(self) -> None:
        self.hass: Any = MagicMock()

    def async_show_form(
        self,
        step_id: str,
        data_schema: Any = None,
        errors: dict | None = None,
        description_placeholders: dict | None = None,
    ) -> dict:
        return {
            "type": "form",
            "step_id": step_id,
            "data_schema": data_schema,
            "errors": errors or {},
        }

    def async_create_entry(self, title: str = "", data: dict | None = None) -> dict:
        return {
            "type": "create_entry",
            "title": title,
            "data": data or {},
        }

    @staticmethod
    def async_get_options_flow(config_entry: Any) -> Any:
        return _MockOptionsFlow(config_entry)


class _MockOptionsFlow:
    def __init__(self, config_entry: Any) -> None:
        self._config_entry = config_entry
        self.hass: Any = MagicMock()

    def async_show_form(
        self,
        step_id: str,
        data_schema: Any = None,
        errors: dict | None = None,
    ) -> dict:
        return {
            "type": "form",
            "step_id": step_id,
            "data_schema": data_schema,
            "errors": errors or {},
        }

    def async_create_entry(
        self, data: dict | None = None, title: str | None = None
    ) -> dict:
        return {
            "type": "create_entry",
            "data": data or {},
        }


_ha_core = MagicMock()
_ha_config_entries = MagicMock()
_ha_const = MagicMock()
_ha_helpers = MagicMock()
_ha_helpers_aiohttp = MagicMock()
_ha_helpers_update = MagicMock()
_ha_helpers_entity = MagicMock()
_ha_helpers_selector = MagicMock()
_ha_components = MagicMock()
_ha_components_sensor = MagicMock()
_ha_data_flow = MagicMock()

ha_mocks = {
    "homeassistant": _ha_core,
    "homeassistant.core": _ha_core,
    "homeassistant.config_entries": _ha_config_entries,
    "homeassistant.const": _ha_const,
    "homeassistant.helpers": _ha_helpers,
    "homeassistant.helpers.aiohttp_client": _ha_helpers_aiohttp,
    "homeassistant.helpers.update_coordinator": _ha_helpers_update,
    "homeassistant.helpers.entity_platform": _ha_helpers_entity,
    "homeassistant.helpers.selector": _ha_helpers_selector,
    "homeassistant.components": _ha_components,
    "homeassistant.components.sensor": _ha_components_sensor,
    "homeassistant.data_entry_flow": _ha_data_flow,
}

for mod_name, mod_mock in ha_mocks.items():
    sys.modules[mod_name] = mod_mock

_ha_core.config_entries = _ha_config_entries
_ha_core.const = _ha_const
_ha_core.helpers = _ha_helpers
_ha_core.components = _ha_components
_ha_core.data_entry_flow = _ha_data_flow
_ha_helpers.aiohttp_client = _ha_helpers_aiohttp
_ha_helpers.update_coordinator = _ha_helpers_update
_ha_helpers.entity_platform = _ha_helpers_entity
_ha_helpers.selector = _ha_helpers_selector
_ha_components.sensor = _ha_components_sensor

_ha_core.HomeAssistant = type("HomeAssistant", (), {})
_ha_core.callback = lambda x: x
_ha_config_entries.ConfigEntry = type("ConfigEntry", (), {})
_ha_config_entries.ConfigFlow = _MockConfigFlow
_ha_config_entries.OptionsFlow = _MockOptionsFlow
_ha_const.Platform = type("Platform", (), {})
_ha_const.Platform.SENSOR = "sensor"
_ha_helpers_update.DataUpdateCoordinator = _MockDataUpdateCoordinator
_ha_helpers_update.CoordinatorEntity = _MockCoordinatorEntity
_ha_helpers_entity.AddEntitiesCallback = type("AddEntitiesCallback", (), {})
_ha_data_flow.FlowResult = type("FlowResult", (), {})
_ha_components_sensor.SensorEntity = _MockSensorEntity

NOW = datetime(2025, 6, 1, 12, 0, 0, tzinfo=UTC)


@pytest.fixture
def mock_hass():
    hass = MagicMock()
    hass.data = {}
    return hass


@pytest.fixture
def sample_offer_raw():
    return {
        "id": "offer-1",
        "price": 9.99,
        "oldPrice": 14.99,
        "referencePrice": 12.99,
        "description": "Franziskaner Weissbier",
        "brand": {"name": "Franziskaner"},
        "product": {
            "name": "Franziskaner Weissbier 500ml",
            "images": [{"url": "https://example.com/franziskaner.jpg"}],
        },
        "advertisers": [{"name": "REWE"}],
        "validityDates": [
            {
                "from": "2025-05-26T00:00:00+02:00",
                "to": "2025-06-07T23:59:59+02:00",
            }
        ],
    }


@pytest.fixture
def sample_offer_raw_2():
    return {
        "id": "offer-2",
        "price": 12.99,
        "oldPrice": 15.99,
        "referencePrice": None,
        "description": "Franziskaner Weissbier Dunkel",
        "brand": {"name": "Franziskaner"},
        "product": {
            "name": "Franziskaner Dunkel 500ml",
            "images": [{"url": "https://example.com/franziskaner-dunkel.jpg"}],
        },
        "advertisers": [{"name": "Kaufland"}],
        "validityDates": [
            {
                "from": "2025-05-26T00:00:00+02:00",
                "to": "2025-06-07T23:59:59+02:00",
            }
        ],
    }


@pytest.fixture
def sample_offer_raw_expired():
    return {
        "id": "offer-expired",
        "price": 7.99,
        "oldPrice": None,
        "referencePrice": None,
        "description": "Franziskaner Weissbier",
        "brand": {"name": "Franziskaner"},
        "product": {
            "name": "Franziskaner Weissbier 500ml",
            "images": [],
        },
        "advertisers": [{"name": "REWE"}],
        "validityDates": [
            {
                "from": "2025-01-01T00:00:00+01:00",
                "to": "2025-01-31T23:59:59+01:00",
            }
        ],
    }


@pytest.fixture
def sample_offer_raw_online():
    return {
        "id": "offer-online",
        "price": 8.99,
        "oldPrice": None,
        "referencePrice": None,
        "description": "Franziskaner online Angebot",
        "brand": {"name": "Franziskaner"},
        "product": {
            "name": "Franziskaner Weissbier",
            "images": [],
        },
        "advertisers": [{"name": "REWE"}],
        "validityDates": [
            {
                "from": "2025-05-26T00:00:00+02:00",
                "to": "2025-06-07T23:59:59+02:00",
            }
        ],
    }


@pytest.fixture
def sample_offer_raw_wrong_retailer():
    return {
        "id": "offer-other",
        "price": 6.99,
        "oldPrice": None,
        "referencePrice": None,
        "description": "Franziskaner Weissbier",
        "brand": {"name": "Franziskaner"},
        "product": {
            "name": "Franziskaner Weissbier",
            "images": [],
        },
        "advertisers": [{"name": "SomeUnknownStore"}],
        "validityDates": [
            {
                "from": "2025-05-26T00:00:00+02:00",
                "to": "2025-06-07T23:59:59+02:00",
            }
        ],
    }


@pytest.fixture
def sample_api_response(sample_offer_raw, sample_offer_raw_2):
    return {
        "results": [sample_offer_raw, sample_offer_raw_2],
    }
