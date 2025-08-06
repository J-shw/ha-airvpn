"""Platform for <your_integration_name> sensor."""
import logging
import asyncio
import aiohttp
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# Polling frequency set to 600 seconds
SCAN_INTERVAL = timedelta(seconds=600)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    api_endpoint = "https://airvpn.org/api/userinfo/?key={api_key}"
    
    async def async_update_data():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_endpoint) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="airvpn_sensor",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )
    
    await coordinator.async_refresh()

    async_add_entities([MyCustomSensor(coordinator, "AirVPN Expiration Days")], True)

class MyCustomSensor(SensorEntity):
    def __init__(self, coordinator, name):
        self._name = name
        self.coordinator = coordinator
        self._state = None
        self._attr_unique_id = f"airvpn_{name}"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self.coordinator.data.get('user', {}).get('expiration_days')

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )