from __future__ import annotations

from datetime import UTC, date, datetime

from custom_components.marktguru.models import Offer, _parse_datetime, _round_to_date


class TestOfferFromApi:
    def test_basic_parsing(self, sample_offer_raw):
        offer = Offer.from_api(sample_offer_raw)
        assert offer.id == "offer-1"
        assert offer.price == 9.99
        assert offer.old_price == 14.99
        assert offer.reference_price == 12.99
        assert offer.description == "Franziskaner Weissbier"
        assert offer.brand_name == "Franziskaner"
        assert offer.product_name == "Franziskaner Weissbier 500ml"
        assert offer.retailer_name == "REWE"
        assert offer.image_url == "https://mg2de.b-cdn.net/api/v1/offers/offer-1/images/default/0/large.jpg"

    def test_parsing_with_timezone(self, sample_offer_raw):
        offer = Offer.from_api(sample_offer_raw)
        assert offer.valid_from is not None
        assert offer.valid_to is not None
        assert isinstance(offer.valid_from, date)
        assert isinstance(offer.valid_to, date)

    def test_missing_advertisers(self):
        data = {
            "id": "test",
            "price": 5.0,
            "description": "Test",
            "validityDates": [],
        }
        offer = Offer.from_api(data)
        assert offer.retailer_name == "Unbekannt"

    def test_missing_brand(self):
        data = {
            "id": "test",
            "price": 5.0,
            "description": "Test",
            "advertisers": [{"name": "REWE"}],
            "validityDates": [],
        }
        offer = Offer.from_api(data)
        assert offer.brand_name is None

    def test_missing_product_images(self):
        data = {
            "id": "test",
            "price": 5.0,
            "description": "Test",
            "advertisers": [{"name": "REWE"}],
            "product": {"name": "Test Product"},
            "validityDates": [],
        }
        offer = Offer.from_api(data)
        assert offer.image_url is None

    def test_empty_validity_dates(self):
        data = {
            "id": "test",
            "price": 5.0,
            "description": "Test",
            "advertisers": [{"name": "REWE"}],
            "validityDates": [],
        }
        offer = Offer.from_api(data)
        assert offer.valid_from is None

    def test_no_validity_dates_key(self):
        data = {
            "id": "test",
            "price": 5.0,
            "description": "Test",
            "advertisers": [{"name": "REWE"}],
        }
        offer = Offer.from_api(data)
        assert offer.valid_from is None

    def test_to_dict(self, sample_offer_raw):
        offer = Offer.from_api(sample_offer_raw)
        d = offer.to_dict()
        assert d["price"] == 9.99
        assert d["description"] == "Franziskaner Weissbier"
        assert d["retailer_name"] == "REWE"
        assert d["image_url"] == "https://mg2de.b-cdn.net/api/v1/offers/offer-1/images/default/0/large.jpg"
        assert d["valid_from"] is not None
        assert d["valid_to"] is not None

    def test_to_dict_missing_dates(self):
        offer = Offer(
            id="test",
            price=5.0,
            description="Test",
            retailer_name="REWE",
            valid_from=None,
            valid_to=None,
        )
        d = offer.to_dict()
        assert d["valid_from"] is None
        assert d["valid_to"] is None


class TestOfferValidity:
    def test_valid_now(self, sample_offer_raw):
        offer = Offer.from_api(sample_offer_raw)
        now = date(2025, 6, 1)
        assert offer.is_valid_now(now)

    def test_expired(self, sample_offer_raw_expired):
        offer = Offer.from_api(sample_offer_raw_expired)
        now = date(2025, 6, 1)
        assert not offer.is_valid_now(now)

    def test_before_start(self, sample_offer_raw):
        offer = Offer.from_api(sample_offer_raw)
        now = date(2025, 5, 1)
        assert not offer.is_valid_now(now)

    def test_none_dates(self):
        offer = Offer(
            id="test",
            price=5.0,
            description="Test",
            retailer_name="REWE",
            valid_from=None,
            valid_to=None,
        )
        assert not offer.is_valid_now()


class TestOfferExclusion:
    def test_not_excluded(self, sample_offer_raw):
        offer = Offer.from_api(sample_offer_raw)
        assert not offer.is_excluded(["online", "app-coupon"])

    def test_excluded_online(self, sample_offer_raw_online):
        offer = Offer.from_api(sample_offer_raw_online)
        assert offer.is_excluded(["online", "app-coupon"])

    def test_excluded_app_coupon(self):
        data = {
            "id": "test",
            "price": 5.0,
            "description": "Special app-coupon deal",
            "advertisers": [{"name": "REWE"}],
            "validityDates": [],
        }
        offer = Offer.from_api(data)
        assert offer.is_excluded(["online", "app-coupon"])

    def test_empty_keywords(self, sample_offer_raw):
        offer = Offer.from_api(sample_offer_raw)
        assert not offer.is_excluded([])


class TestParseDatetime:
    def test_iso_with_timezone(self):
        dt = _parse_datetime("2025-06-01T12:00:00+02:00")
        assert dt.year == 2025
        assert dt.month == 6
        assert dt.tzinfo is not None

    def test_iso_utc(self):
        dt = _parse_datetime("2025-06-01T12:00:00Z")
        assert dt.year == 2025
        assert dt.tzinfo is not None

    def test_date_only(self):
        dt = _parse_datetime("2025-06-01")
        assert dt.year == 2025
        assert dt.month == 6

    def test_empty_string(self):
        dt = _parse_datetime("")
        assert dt is None

    def test_invalid_format(self):
        dt = _parse_datetime("not-a-date")
        assert dt is None


class TestRoundToDate:
    def test_valid_from_before_noon(self):
        dt = datetime(2026, 6, 1, 10, 0, 0, tzinfo=UTC)
        assert _round_to_date(dt, is_start=True) == date(2026, 6, 1)

    def test_valid_from_at_noon(self):
        dt = datetime(2026, 6, 1, 12, 0, 0, tzinfo=UTC)
        assert _round_to_date(dt, is_start=True) == date(2026, 6, 2)

    def test_valid_from_after_noon(self):
        dt = datetime(2026, 5, 31, 22, 0, 0, tzinfo=UTC)
        assert _round_to_date(dt, is_start=True) == date(2026, 6, 1)

    def test_valid_to_before_noon(self):
        dt = datetime(2026, 6, 7, 9, 0, 0, tzinfo=UTC)
        assert _round_to_date(dt, is_start=False) == date(2026, 6, 6)

    def test_valid_to_at_noon(self):
        dt = datetime(2026, 6, 7, 12, 0, 0, tzinfo=UTC)
        assert _round_to_date(dt, is_start=False) == date(2026, 6, 7)

    def test_valid_to_after_noon(self):
        dt = datetime(2026, 6, 6, 21, 59, 0, tzinfo=UTC)
        assert _round_to_date(dt, is_start=False) == date(2026, 6, 6)

    def test_none(self):
        assert _round_to_date(None, is_start=True) is None
        assert _round_to_date(None, is_start=False) is None
