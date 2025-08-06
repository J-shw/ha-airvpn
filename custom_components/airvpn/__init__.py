import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, CONF_API_KEY

DOMAIN = "airvpn"
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.info("Setting up AirVPN integration")

    api_key = entry.data["api_key"]
    hass.data.setdefault(DOMAIN, {})[CONF_API_KEY] = api_key

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    return True