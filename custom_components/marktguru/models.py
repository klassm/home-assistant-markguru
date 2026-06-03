from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass
class Offer:
    id: str
    price: float
    description: str
    retailer_name: str
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    old_price: float | None = None
    reference_price: float | None = None
    brand_name: str | None = None
    product_name: str | None = None
    image_url: str | None = None

    @staticmethod
    def from_api(data: dict[str, Any]) -> Offer:
        validity = data.get("validityDates", [{}])
        validity_first = validity[0] if validity else {}
        valid_from_str = validity_first.get("from", "")
        valid_to_str = validity_first.get("to", "")

        valid_from = _parse_datetime(valid_from_str)
        valid_to = _parse_datetime(valid_to_str)

        advertisers = data.get("advertisers", [{}])
        retailer_name = advertisers[0].get("name") if advertisers else None

        brand = data.get("brand", {})
        brand_name = brand.get("name") if brand else None

        product = data.get("product", {})
        product_name = product.get("name") if product else None

        images = product.get("images", []) if product else []
        image_url = images[0].get("url") if images else None

        return Offer(
            id=data.get("id", ""),
            price=data.get("price", 0.0),
            description=data.get("description", ""),
            retailer_name=retailer_name or "Unbekannt",
            valid_from=valid_from,
            valid_to=valid_to,
            old_price=data.get("oldPrice"),
            reference_price=data.get("referencePrice"),
            brand_name=brand_name,
            product_name=product_name,
            image_url=image_url,
        )

    def is_valid_now(self, now: datetime | None = None) -> bool:
        if self.valid_from is None or self.valid_to is None:
            return False
        if now is None:
            now = datetime.now().astimezone()
        valid_from = (
            self.valid_from
            if self.valid_from.tzinfo
            else self.valid_from.replace(tzinfo=now.tzinfo)
        )
        valid_to = (
            self.valid_to
            if self.valid_to.tzinfo
            else self.valid_to.replace(tzinfo=now.tzinfo)
        )
        return valid_from <= now <= valid_to

    def is_excluded(self, exclude_keywords: list[str]) -> bool:
        desc_lower = self.description.lower()
        return any(kw in desc_lower for kw in exclude_keywords)

    def to_dict(self) -> dict[str, Any]:
        return {
            "price": self.price,
            "old_price": self.old_price,
            "reference_price": self.reference_price,
            "description": self.description,
            "brand_name": self.brand_name,
            "product_name": self.product_name,
            "retailer_name": self.retailer_name,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_to": self.valid_to.isoformat() if self.valid_to else None,
            "image_url": self.image_url,
        }


def _parse_datetime(value: str) -> datetime | None:
    if not value:
        return None
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(value, fmt)
            if not dt.tzinfo:
                dt = dt.replace(tzinfo=UTC)
            return dt
        except ValueError:
            continue
    return None
