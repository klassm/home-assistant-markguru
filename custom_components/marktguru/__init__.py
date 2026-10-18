from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api_client import MarktguruClient
from .const import (
    CONF_ALLOWED_RETAILERS,
    CONF_API_KEY,
    CONF_CLIENT_KEY,
    CONF_PRODUCTS,
    CONF_SCAN_INTERVAL,
    CONF_ZIP_CODE,
    CONFIG_VERSION,
    DEFAULT_ALLOWED_RETAILERS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import MarktguruDataUpdateCoordinator

PLATFORMS = [Platform.SENSOR]


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if entry.version > CONFIG_VERSION:
        return False

    if entry.version < CONFIG_VERSION:
        data = {
            key: value
            for key, value in entry.data.items()
            if key not in (CONF_CLIENT_KEY, CONF_API_KEY)
        }
        products = data.get(CONF_PRODUCTS)
        if isinstance(products, str):
            data[CONF_PRODUCTS] = [
                p.strip() for p in products.split(",") if p.strip()
            ]
        hass.config_entries.async_update_entry(
            entry, data=data, version=CONFIG_VERSION
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    client = MarktguruClient(
        session=async_get_clientsession(hass),
        client_key=entry.data.get(CONF_CLIENT_KEY) or None,
        api_key=entry.data.get(CONF_API_KEY) or None,
    )

    products = entry.options.get(CONF_PRODUCTS, entry.data.get(CONF_PRODUCTS, []))
    allowed_retailers = entry.options.get(
        CONF_ALLOWED_RETAILERS,
        entry.data.get(CONF_ALLOWED_RETAILERS, DEFAULT_ALLOWED_RETAILERS),
    )
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL,
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )

    coordinator = MarktguruDataUpdateCoordinator(
        hass=hass,
        client=client,
        zip_code=entry.data[CONF_ZIP_CODE],
        products=products,
        allowed_retailers=allowed_retailers,
        scan_interval=int(scan_interval),
    )

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
