from __future__ import annotations

import logging
from datetime import date, datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api_client import MarktguruApiError, MarktguruClient
from .const import (
    EXCLUDE_KEYWORDS,
)
from .models import Offer

logger = logging.getLogger(__name__)


class MarktguruDataUpdateCoordinator(DataUpdateCoordinator[dict[str, list[Offer]]]):
    def __init__(
        self,
        hass: HomeAssistant,
        client: MarktguruClient,
        zip_code: str,
        products: list[str],
        allowed_retailers: list[str],
        scan_interval: int,
    ) -> None:
        self._client = client
        self._zip_code = zip_code
        self._products = products
        self._allowed_retailers = allowed_retailers

        super().__init__(
            hass,
            logger,
            name="marktguru",
            update_interval=timedelta(hours=scan_interval),
        )

    @property
    def zip_code(self) -> str:
        return self._zip_code

    @property
    def products(self) -> list[str]:
        return self._products

    @property
    def allowed_retailers(self) -> list[str]:
        return self._allowed_retailers

    async def _async_update_data(self) -> dict[str, list[Offer]]:
        result: dict[str, list[Offer]] = {}
        for query in self._products:
            try:
                offers = await self._client.search_offers(query, self._zip_code)
            except MarktguruApiError as err:
                raise UpdateFailed(err) from err
            filtered = _filter_offers(offers, self._allowed_retailers, EXCLUDE_KEYWORDS)
            sorted_offers = sorted(filtered, key=lambda o: o.price)
            result[query] = sorted_offers
        return result


def _filter_offers(
    offers: list[Offer],
    allowed_retailers: list[str],
    exclude_keywords: list[str],
    now: date | None = None,
) -> list[Offer]:
    filtered: list[Offer] = []
    for offer in offers:
        if not offer.is_valid_now(now):
            continue
        if offer.retailer_name not in allowed_retailers:
            continue
        if offer.is_excluded(exclude_keywords):
            continue
        filtered.append(offer)
    return filtered
