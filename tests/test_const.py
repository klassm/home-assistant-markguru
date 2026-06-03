from __future__ import annotations

from custom_components.marktguru.const import (
    API_LIMIT,
    API_URL,
    DEFAULT_ALLOWED_RETAILERS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    EXCLUDE_KEYWORDS,
    KNOWN_RETAILERS,
)


class TestConstants:
    def test_domain(self):
        assert DOMAIN == "marktguru"

    def test_default_scan_interval(self):
        assert DEFAULT_SCAN_INTERVAL == 12

    def test_default_allowed_retailers(self):
        assert "REWE" in DEFAULT_ALLOWED_RETAILERS
        assert "Kaufland" in DEFAULT_ALLOWED_RETAILERS
        assert "EDEKA" in DEFAULT_ALLOWED_RETAILERS
        assert len(DEFAULT_ALLOWED_RETAILERS) == 5

    def test_known_retailers_contains_defaults(self):
        for retailer in DEFAULT_ALLOWED_RETAILERS:
            assert retailer in KNOWN_RETAILERS

    def test_exclude_keywords(self):
        assert "online" in EXCLUDE_KEYWORDS
        assert "app-coupon" in EXCLUDE_KEYWORDS

    def test_api_url(self):
        assert API_URL == "https://api.marktguru.de/api/v1/offers/search"

    def test_api_limit(self):
        assert API_LIMIT == 24
