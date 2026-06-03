from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

from custom_components.marktguru.models import Offer
from custom_components.marktguru.sensor import NO_OFFER_TEXT, MarktguruOfferSensor


def _make_coordinator(data, zip_code="86156", products=None):
    coordinator = MagicMock()
    coordinator.data = data
    coordinator.zip_code = zip_code
    coordinator.products = products or ["Franziskaner"]
    return coordinator


def _make_offer(
    offer_id="offer-1",
    price=9.99,
    description="Franziskaner Weissbier",
    retailer_name="REWE",
    valid_from=None,
    valid_to=None,
    image_url="https://example.com/img.jpg",
    old_price=14.99,
    reference_price=12.99,
    brand_name="Franziskaner",
    product_name="Franziskaner Weissbier 500ml",
):
    if valid_from is None:
        valid_from = date(2025, 5, 26)
    if valid_to is None:
        valid_to = date(2025, 6, 7)
    return Offer(
        id=offer_id,
        price=price,
        description=description,
        retailer_name=retailer_name,
        valid_from=valid_from,
        valid_to=valid_to,
        image_url=image_url,
        old_price=old_price,
        reference_price=reference_price,
        brand_name=brand_name,
        product_name=product_name,
    )


class TestMarktguruOfferSensor:
    def test_native_value_with_offers(self):
        offer1 = _make_offer(price=9.99)
        offer2 = _make_offer(offer_id="offer-2", price=12.99)
        coordinator = _make_coordinator({"Franziskaner": [offer1, offer2]})
        sensor = MarktguruOfferSensor(
            coordinator=coordinator,
            query="Franziskaner",
            zip_code="86156",
        )
        assert sensor.native_value == 9.99

    def test_native_value_no_offers(self):
        coordinator = _make_coordinator({"Franziskaner": []})
        sensor = MarktguruOfferSensor(
            coordinator=coordinator,
            query="Franziskaner",
            zip_code="86156",
        )
        assert sensor.native_value == NO_OFFER_TEXT

    def test_native_value_no_data(self):
        coordinator = _make_coordinator(None)
        sensor = MarktguruOfferSensor(
            coordinator=coordinator,
            query="Franziskaner",
            zip_code="86156",
        )
        assert sensor.native_value == NO_OFFER_TEXT

    def test_native_value_query_not_in_data(self):
        coordinator = _make_coordinator({"OtherProduct": []})
        sensor = MarktguruOfferSensor(
            coordinator=coordinator,
            query="Franziskaner",
            zip_code="86156",
        )
        assert sensor.native_value == NO_OFFER_TEXT

    def test_attributes_with_offers(self):
        offer1 = _make_offer(price=9.99, description="Best offer")
        offer2 = _make_offer(
            offer_id="offer-2",
            price=12.99,
            description="Second offer",
            retailer_name="Kaufland",
        )
        coordinator = _make_coordinator({"Franziskaner": [offer1, offer2]})
        sensor = MarktguruOfferSensor(
            coordinator=coordinator,
            query="Franziskaner",
            zip_code="86156",
        )
        attrs = sensor.extra_state_attributes
        assert len(attrs["offers"]) == 2
        assert attrs["offers"][0]["price"] == 9.99
        assert attrs["offers"][0]["description"] == "Best offer"
        assert attrs["offers"][0]["retailer_name"] == "REWE"
        assert attrs["offers"][1]["price"] == 12.99
        assert attrs["offers"][1]["description"] == "Second offer"

    def test_attributes_no_offers(self):
        coordinator = _make_coordinator({"Franziskaner": []})
        sensor = MarktguruOfferSensor(
            coordinator=coordinator,
            query="Franziskaner",
            zip_code="86156",
        )
        attrs = sensor.extra_state_attributes
        assert attrs["offers"] == []

    def test_unique_id(self):
        coordinator = _make_coordinator({})
        sensor = MarktguruOfferSensor(
            coordinator=coordinator,
            query="Franziskaner",
            zip_code="86156",
        )
        assert sensor.unique_id == "marktguru_86156_franziskaner"

    def test_name(self):
        coordinator = _make_coordinator({})
        sensor = MarktguruOfferSensor(
            coordinator=coordinator,
            query="Franziskaner",
            zip_code="86156",
        )
        assert sensor.name == "Marktguru Franziskaner (86156)"

    def test_unit_of_measurement(self):
        coordinator = _make_coordinator({})
        sensor = MarktguruOfferSensor(
            coordinator=coordinator,
            query="Franziskaner",
            zip_code="86156",
        )
        assert sensor.native_unit_of_measurement == "€"

    def test_attributes_valid_dates(self):
        offer = _make_offer()
        coordinator = _make_coordinator({"Franziskaner": [offer]})
        sensor = MarktguruOfferSensor(
            coordinator=coordinator,
            query="Franziskaner",
            zip_code="86156",
        )
        attrs = sensor.extra_state_attributes
        assert attrs["offers"][0]["valid_from"] is not None
        assert attrs["offers"][0]["valid_to"] is not None

    def test_single_offer_in_array(self):
        offer = _make_offer()
        coordinator = _make_coordinator({"Franziskaner": [offer]})
        sensor = MarktguruOfferSensor(
            coordinator=coordinator,
            query="Franziskaner",
            zip_code="86156",
        )
        attrs = sensor.extra_state_attributes
        assert len(attrs["offers"]) == 1

    def test_multiple_offers_sorted_by_price(self):
        offers = [
            _make_offer(offer_id=f"offer-{i}", price=9.99 + i * 3) for i in range(4)
        ]
        coordinator = _make_coordinator({"Franziskaner": offers})
        sensor = MarktguruOfferSensor(
            coordinator=coordinator,
            query="Franziskaner",
            zip_code="86156",
        )
        attrs = sensor.extra_state_attributes
        assert sensor.native_value == 9.99
        assert len(attrs["offers"]) == 4
        assert attrs["offers"][0]["price"] == 9.99

    def test_attributes_none_dates(self):
        offer = Offer(
            id="test",
            price=5.99,
            description="No dates",
            retailer_name="REWE",
            valid_from=None,
            valid_to=None,
        )
        coordinator = _make_coordinator({"Franziskaner": [offer]})
        sensor = MarktguruOfferSensor(
            coordinator=coordinator,
            query="Franziskaner",
            zip_code="86156",
        )
        attrs = sensor.extra_state_attributes
        assert attrs["offers"][0]["valid_from"] is None
        assert attrs["offers"][0]["valid_to"] is None
