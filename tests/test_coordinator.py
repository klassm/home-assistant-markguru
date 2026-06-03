from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from custom_components.marktguru.coordinator import (
    MarktguruDataUpdateCoordinator,
    _filter_offers,
)
from custom_components.marktguru.models import Offer

FILTER_NOW = datetime(2025, 6, 1, 12, 0, 0, tzinfo=UTC)

VALID_FROM = datetime(2020, 1, 1, 0, 0, tzinfo=UTC)
VALID_TO = datetime(2030, 12, 31, 23, 59, 59, tzinfo=UTC)


class TestFilterOffers:
    def test_basic_filter(
        self,
        sample_offer_raw,
        sample_offer_raw_2,
        sample_offer_raw_expired,
        sample_offer_raw_online,
        sample_offer_raw_wrong_retailer,
    ):
        offers = [
            Offer.from_api(sample_offer_raw),
            Offer.from_api(sample_offer_raw_2),
            Offer.from_api(sample_offer_raw_expired),
            Offer.from_api(sample_offer_raw_online),
            Offer.from_api(sample_offer_raw_wrong_retailer),
        ]

        filtered = _filter_offers(
            offers, ["REWE", "Kaufland"], ["online", "app-coupon"], now=FILTER_NOW
        )

        assert len(filtered) == 2
        assert filtered[0].retailer_name == "REWE"
        assert filtered[1].retailer_name == "Kaufland"

    def test_all_expired(self, sample_offer_raw_expired):
        offers = [Offer.from_api(sample_offer_raw_expired)]
        filtered = _filter_offers(offers, ["REWE"], ["online"], now=FILTER_NOW)
        assert len(filtered) == 0

    def test_no_allowed_retailers_match(self, sample_offer_raw_wrong_retailer):
        offers = [Offer.from_api(sample_offer_raw_wrong_retailer)]
        filtered = _filter_offers(offers, ["REWE"], ["online"], now=FILTER_NOW)
        assert len(filtered) == 0

    def test_empty_offers_list(self):
        filtered = _filter_offers([], ["REWE"], ["online"], now=FILTER_NOW)
        assert len(filtered) == 0

    def test_online_offer_excluded(self, sample_offer_raw_online):
        offers = [Offer.from_api(sample_offer_raw_online)]
        filtered = _filter_offers(
            offers, ["REWE"], ["online", "app-coupon"], now=FILTER_NOW
        )
        assert len(filtered) == 0

    def test_no_exclude_keywords(self, sample_offer_raw_online):
        offers = [Offer.from_api(sample_offer_raw_online)]
        filtered = _filter_offers(offers, ["REWE"], [], now=FILTER_NOW)
        assert len(filtered) == 1

    def test_none_dates_filtered_out(self):
        offer = Offer(
            id="test",
            price=5.0,
            description="Test",
            retailer_name="REWE",
            valid_from=None,
            valid_to=None,
        )
        filtered = _filter_offers([offer], ["REWE"], [], now=FILTER_NOW)
        assert len(filtered) == 0


class TestCoordinator:
    @pytest.mark.asyncio
    async def test_async_update_data(self, mock_hass):
        from custom_components.marktguru.api_client import MarktguruClient

        client = AsyncMock(spec=MarktguruClient)
        offer1 = Offer(
            id="offer-1",
            price=9.99,
            description="Franziskaner Weissbier",
            retailer_name="REWE",
            valid_from=VALID_FROM,
            valid_to=VALID_TO,
            image_url="https://example.com/img.jpg",
        )
        offer2 = Offer(
            id="offer-2",
            price=12.99,
            description="Franziskaner Dunkel",
            retailer_name="Kaufland",
            valid_from=VALID_FROM,
            valid_to=VALID_TO,
        )
        client.search_offers.return_value = [offer2, offer1]

        coordinator = MarktguruDataUpdateCoordinator(
            hass=mock_hass,
            client=client,
            zip_code="86156",
            products=["Franziskaner"],
            allowed_retailers=["REWE", "Kaufland"],
            scan_interval=12,
        )

        data = await coordinator._async_update_data()

        assert "Franziskaner" in data
        assert len(data["Franziskaner"]) == 2
        assert data["Franziskaner"][0].price == 9.99
        assert data["Franziskaner"][1].price == 12.99

    @pytest.mark.asyncio
    async def test_multiple_products(self, mock_hass):
        from custom_components.marktguru.api_client import MarktguruClient

        client = AsyncMock(spec=MarktguruClient)
        offer_a = Offer(
            id="a",
            price=5.99,
            description="Product A",
            retailer_name="REWE",
            valid_from=VALID_FROM,
            valid_to=VALID_TO,
        )
        offer_b = Offer(
            id="b",
            price=3.99,
            description="Product B",
            retailer_name="Kaufland",
            valid_from=VALID_FROM,
            valid_to=VALID_TO,
        )

        async def mock_search(query, zip_code):
            if query == "ProductA":
                return [offer_a]
            return [offer_b]

        client.search_offers.side_effect = mock_search

        coordinator = MarktguruDataUpdateCoordinator(
            hass=mock_hass,
            client=client,
            zip_code="86156",
            products=["ProductA", "ProductB"],
            allowed_retailers=["REWE", "Kaufland"],
            scan_interval=12,
        )

        data = await coordinator._async_update_data()

        assert "ProductA" in data
        assert "ProductB" in data
        assert len(data["ProductA"]) == 1
        assert len(data["ProductB"]) == 1
