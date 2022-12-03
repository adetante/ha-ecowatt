"""The ecowatt integration."""
from __future__ import annotations
from datetime import timedelta

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_CLIENT_ID, CONF_CLIENT_SECRET
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from pyecowatt.pyecowatt import Ecowatt

from .const import DOMAIN, COORDINATOR_ECOWATT

PLATFORMS: list[Platform] = [Platform.SENSOR]
SCAN_INTERVAL = timedelta(minutes=60)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ecowatt from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    client_id = entry.data[CONF_CLIENT_ID]
    client_secret = entry.data[CONF_CLIENT_SECRET]

    client = Ecowatt(client_id, client_secret)

    async def _async_update_data_ecowatt():
        """Fetch data from API endpoint."""
        return await client.get_signals()

    coordinator_ecowatt = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Ecowatt",
        update_method=_async_update_data_ecowatt,
        update_interval=SCAN_INTERVAL,
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator_ecowatt.async_refresh()

    if not coordinator_ecowatt.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = {
        COORDINATOR_ECOWATT: coordinator_ecowatt,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)

    return unload_ok
