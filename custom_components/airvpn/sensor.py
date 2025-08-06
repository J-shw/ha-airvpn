import logging
import asyncio
import aiohttp
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.components.binary_sensor import BinarySensorEntity
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

    user_data = coordinator.data.get('user', {})
    username = user_data.get('login')
    user_device_id = username.lower() if username else None

    user_sensors = []
    user_binary_sensors = []

    if user_device_id:
        user_sensors = [
            AirVPNUserSensor(coordinator, "Expiration Days", "expiration_days", user_device_id, username, "days", "mdi:calendar-end", SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT),
            AirVPNUserSensor(coordinator, "Credits", "credits", user_device_id, username, icon="mdi:bitcoin", device_class=SensorDeviceClass.MONETARY, state_class=SensorStateClass.MEASUREMENT),
            AirVPNUserSensor(coordinator, "Last Activity", "last_activity_date", user_device_id, username, icon="mdi:clock-end"),
            AirVPNUserSensor(coordinator, "Username", "login", user_device_id, username, icon="mdi:account"),
        ]
        
        user_binary_sensors = [
            AirVPNUserBinarySensor(coordinator, "Connected", "connected", user_device_id, username, icon="mdi:vpn"),
            AirVPNUserBinarySensor(coordinator, "Premium", "premium", user_device_id, username, icon="mdi:crown"),
        ]

    session_sensors = []
    sessions_data = coordinator.data.get('sessions', [])
    for session in sessions_data:
        device_name = session.get('device_name')
        session_id = device_name
        if session_id:
            session_sensors.append(AirVPNSessionSensor(coordinator, session, "Server Name", "server_name", "mdi:server-network", session_id, device_name=device_name))
            session_sensors.append(AirVPNSessionSensor(coordinator, session, "VPN IP", "vpn_ip", "mdi:ip-network", session_id, device_name=device_name))
            session_sensors.append(AirVPNSessionSensor(coordinator, session, "Entry IP", "entry_ip", "mdi:ip-network-outline", session_id, device_name=device_name))
            session_sensors.append(AirVPNSessionSensor(coordinator, session, "Exit IP", "exit_ip", "mdi:ip-network-outline", session_id, device_name=device_name))
            session_sensors.append(AirVPNSessionSensor(coordinator, session, "Server Country", "server_country", "mdi:earth", session_id, device_name=device_name))
            session_sensors.append(AirVPNSessionSensor(coordinator, session, "Connected Since", "connected_since_date", "mdi:clock-start", session_id, device_name=device_name))
            session_sensors.append(AirVPNSessionSensor(coordinator, session, "Bytes Read", "bytes_read", "mdi:download", session_id, unit="bytes", device_class=SensorDeviceClass.DATA_SIZE, device_name=device_name))
            session_sensors.append(AirVPNSessionSensor(coordinator, session, "Bytes Written", "bytes_write", "mdi:upload", session_id, unit="bytes", device_class=SensorDeviceClass.DATA_SIZE, device_name=device_name))
            session_sensors.append(AirVPNSessionSensor(coordinator, session, "Read Speed", "speed_read", "mdi:download-network", session_id, unit="B/s", device_class=SensorDeviceClass.DATA_RATE, device_name=device_name))
            session_sensors.append(AirVPNSessionSensor(coordinator, session, "Write Speed", "speed_write", "mdi:upload-network", session_id, unit="B/s", device_class=SensorDeviceClass.DATA_RATE, device_name=device_name))
            session_sensors.append(AirVPNSessionSensor(coordinator, session, "Server Bandwidth", "server_bw", "mdi:chart-bell-curve", session_id, unit="Mbit/s", device_class=SensorDeviceClass.DATA_RATE, state_class=SensorStateClass.MEASUREMENT, device_name=device_name))

    async_add_entities(user_sensors, True)
    async_add_entities(user_binary_sensors, True)
    async_add_entities(session_sensors, True)

class AirVPNUserSensor(SensorEntity):
    def __init__(self, coordinator, name, key, device_id, device_name, unit=None, icon=None, device_class=None, state_class=None):
        self._name = name
        self.coordinator = coordinator
        self._key = key
        self._attr_unique_id = f"airvpn_user_{key}"
        self._attr_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_device_class = device_class
        self._attr_state_class = state_class

        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": f"AirVPN User ({device_name})",
            "manufacturer": "AirVPN",
        }

    @property
    def name(self):
        return f"AirVPN {self._name}"
    
    @property
    def state(self):
        """Return the state of the sensor."""
        user_data = self.coordinator.data.get('user', {})
        return user_data.get(self._key)

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

class AirVPNUserBinarySensor(BinarySensorEntity):
    def __init__(self, coordinator, name, key, device_id, device_name, icon=None):
        self._name = name
        self.coordinator = coordinator
        self._key = key
        self._attr_unique_id = f"airvpn_user_{key}"
        self._attr_icon = icon
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": f"AirVPN User ({device_name})",
            "manufacturer": "AirVPN",
        }

    @property
    def name(self):
        return f"AirVPN {self._name}"

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        user_data = self.coordinator.data.get('user', {})
        return user_data.get(self._key)

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

class AirVPNSessionSensor(SensorEntity):
    def __init__(self, coordinator, session_data, name, key, icon, device_id, unit=None, device_class=None, device_name=None, state_class=None):
        self.coordinator = coordinator
        self._session_data = session_data
        self._name = name
        self._key = key
        self._attr_unique_id = f"airvpn_session_{device_id}_{key}"
        self._attr_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": f"AirVPN Session ({device_name})",
            "manufacturer": "AirVPN",
        }

    @property
    def name(self):
        return self._name
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._session_data.get(self._key)

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )