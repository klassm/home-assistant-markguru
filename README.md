# Home Assistant Marktguru Integration

Track product offers from German retailers using the Marktguru API.

## Features

- Track multiple products by search query
- Filter offers by allowed retailers (REWE, Kaufland, EDEKA, etc.)
- Automatically exclude online-only and app-coupon offers
- Show the lowest valid price as sensor state
- Additional offers with higher prices as attributes
- Product images as attributes for nice dashboard cards
- Configurable update interval (1-24 hours)

## Installation

### HACS

Add this repository as a custom repository in HACS, then install the integration.

### Manual

Copy the `custom_components/marktguru/` directory to your Home Assistant `custom_components/` directory.

## Configuration

1. Go to **Settings** > **Devices & Services** > **Add Integration**
2. Search for **Marktguru**
3. Enter your zip code, client key, and API key
4. Configure products to track and allowed retailers

### Config Fields

| Field | Description |
|-------|-------------|
| Zip Code | Your postal code for location-based offers |
| Client Key | The `x-clientkey` header value (optional — built-in defaults are used if left empty) |
| API Key | The `x-apikey` header value (optional — built-in defaults are used if left empty) |
| Products | Search terms, added one by one via the "Add item" field |
| Allowed Retailers | Select which retailers to include |
| Update Interval | How often to check for new offers (1-24 hours, default 12) |

## Sensor

Each product query creates one sensor:

- **State**: Lowest price among valid offers, or "Kein Angebot" if none found
- **Attributes**:
  - `description` - Offer description
  - `vendor` - Retailer name
  - `valid_from` / `valid_to` - Offer validity dates
  - `image_url` - Product image URL
  - `additional_offers` - List of higher-priced valid offers

### Example Dashboard Card

```yaml
type: entity
entity: sensor.marktguru_franziskaner_86156
```

## Obtaining API Keys

The integration ships with the public keys used by the Marktguru web app, so you normally don't need to enter anything here. If the built-in keys stop working (Marktguru occasionally rotates them), you can extract the current `x-clientkey` and `x-apikey` header values from the Marktguru web app yourself. See the [ha-marktguru](https://github.com/thorschtn/ha-marktguru) project for reference.
