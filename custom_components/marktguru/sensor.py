from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MarktguruDataUpdateCoordinator
from .models import Offer

NO_OFFER_TEXT = "Kein Angebot"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MarktguruDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[MarktguruOfferSensor] = []
    for query in coordinator.products:
        entities.append(
            MarktguruOfferSensor(
                coordinator=coordinator,
                query=query,
                zip_code=coordinator.zip_code,
            )
        )

    async_add_entities(entities)


class MarktguruOfferSensor(
    CoordinatorEntity[MarktguruDataUpdateCoordinator], SensorEntity
):
    def __init__(
        self,
        coordinator: MarktguruDataUpdateCoordinator,
        query: str,
        zip_code: str,
    ) -> None:
        super().__init__(coordinator)
        self._query = query
        self._zip_code = zip_code
        self._attr_unique_id = f"marktguru_{zip_code}_{query.lower().replace(' ', '_')}"
        self._attr_name = f"Marktguru {query} ({zip_code})"
        self._attr_device_class = None
        self._attr_native_unit_of_measurement = "€"

    @property
    def native_value(self) -> str | float | None:
        offers = self._get_offers()
        if not offers:
            return NO_OFFER_TEXT
        return offers[0].price

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        offers = self._get_offers()
        if not offers:
            return {
                "description": None,
                "vendor": None,
                "valid_from": None,
                "valid_to": None,
                "image_url": None,
                "additional_offers": [],
            }

        best = offers[0]
        additional = [o.to_dict() for o in offers[1:]]

        return {
            "description": best.description,
            "vendor": best.retailer_name,
            "valid_from": best.valid_from.isoformat() if best.valid_from else None,
            "valid_to": best.valid_to.isoformat() if best.valid_to else None,
            "image_url": best.image_url,
            "additional_offers": additional,
        }

    def _get_offers(self) -> list[Offer]:
        if self.coordinator.data is None:
            return []
        return self.coordinator.data.get(self._query, [])
