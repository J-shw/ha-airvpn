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

from .const import DOMAIN, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=600)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):

    api_key = hass.data[DOMAIN][CONF_API_KEY]

    api_endpoint = f"https://airvpn.org/api/userinfo/?key={api_key}"
    
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
        name="airvpn_coordinator",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )
    
    await coordinator.async_refresh()

    sensors = [
        AirVPNUserSensor(coordinator, "Expiration Days", "expiration_days", "days"),
        AirVPNUserSensor(coordinator, "Last Activity", "last_activity_date"),
        AirVPNUserSensor(coordinator, "Connected", "connected"),
        AirVPNUserSensor(coordinator, "Username", "login"),
        AirVPNUserSensor(coordinator, "Premium", "premium"),
        AirVPNUserSensor(coordinator, "Credits", "credits"),
    ]

    async_add_entities(sensors, True)

class AirVPNUserSensor(SensorEntity):
    def __init__(self, coordinator, name, key, unit=None):
        self._name = name
        self.coordinator = coordinator
        self._key = key
        self._attr_unique_id = f"airvpn_user_{key}"
        self._attr_unit_of_measurement = unit

    @property
    def name(self):
        return f"AirVPN {self._name}"

    @property
    def state(self):
        user_data = self.coordinator.data.get('user', {})
        return user_data.get(self._key)

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )