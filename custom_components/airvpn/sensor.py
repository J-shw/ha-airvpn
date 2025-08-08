import logging
import asyncio
import aiohttp
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed, CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=300)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):

    api_key = hass.data[DOMAIN][CONF_API_KEY]

    api_endpoint_userinfo  = f"https://airvpn.org/api/userinfo/?key={api_key}"
    api_endpoint_devices = f"https://airvpn.org/api/devices/?key={api_key}"
    
    async def async_update_data():
        try:
            async with aiohttp.ClientSession() as session:
                userinfo_response = await session.get(api_endpoint_userinfo)
                devices_response = await session.get(api_endpoint_devices)

                userinfo_response.raise_for_status()
                devices_response.raise_for_status()

                userinfo_data = await userinfo_response.json()
                devices_data = await devices_response.json()
                
                data = userinfo_data
                data["devices"] = devices_data["devices"] if "devices" in devices_data and devices_data["devices"] else []
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
    
    sessions_by_name = {s.get('device_name'): s for s in coordinator.data.get('sessions', [])}

    session_sensors = []
    device_sensors = []
    for device_info in coordinator.data.get('devices', []):
        device_id = device_info.get('id')
        device_name = device_info.get('name')
        
        if not device_id or not device_name:
            continue

        device_sensors.extend([
            AirVPNDeviceSensor(coordinator, device_info, "Status", "status", "mdi:network-outline", device_id, device_name),
            AirVPNDeviceSensor(coordinator, device_info, "Last Attempt Date", "vpn_attempt_date", "mdi:calendar-check", device_id, device_name),
            AirVPNDeviceSensor(coordinator, device_info, "VPN Last From", "vpn_last_from_date", "mdi:vpn", device_id, device_name),
            AirVPNDeviceSensor(coordinator, device_info, "VPN Last To", "vpn_last_to_date", "mdi:vpn", device_id, device_name),
        ])
        
        session = sessions_by_name.get(device_name)
        if session:
            session_sensors.extend([
                AirVPNSessionSensor(coordinator, device_id, device_name, "server_name", "Server Name", None, "mdi:server-network"),
                AirVPNSessionSensor(coordinator, device_id, device_name, "vpn_ip", "VPN IP", None, "mdi:ip-network"),
                AirVPNSessionSensor(coordinator, device_id, device_name, "entry_ip", "Entry IP", None, "mdi:ip-network-outline"),
                AirVPNSessionSensor(coordinator, device_id, device_name, "exit_ip", "Exit IP", None, "mdi:ip-network-outline"),
                AirVPNSessionSensor(coordinator, device_id, device_name, "server_country", "Server Country", None, "mdi:earth"),
                AirVPNSessionSensor(coordinator, device_id, device_name, "connected_since_date", "Connected Since", None, "mdi:clock-start"),
                AirVPNSessionSensor(coordinator, device_id, device_name, "bytes_read", "Data Downloaded", "bytes", "mdi:download", device_class=SensorDeviceClass.DATA_SIZE),
                AirVPNSessionSensor(coordinator, device_id, device_name, "bytes_write", "Data Uploaded", "bytes", "mdi:upload", device_class=SensorDeviceClass.DATA_SIZE),
                AirVPNSessionSensor(coordinator, device_id, device_name, "speed_read", "Download Speed", "B/s", "mdi:download-network", device_class=SensorDeviceClass.DATA_RATE),
                AirVPNSessionSensor(coordinator, device_id, device_name, "speed_write", "Upload Speed", "B/s", "mdi:upload-network", device_class=SensorDeviceClass.DATA_RATE),
                AirVPNSessionSensor(coordinator, device_id, device_name, "server_bw", "Server Bandwidth", "Mbit/s", "mdi:chart-bell-curve", device_class=SensorDeviceClass.DATA_RATE),
            ])

    async_add_entities(user_sensors, True)
    async_add_entities(user_binary_sensors, True)
    async_add_entities(device_sensors, True)
    async_add_entities(session_sensors, True)

# -- Base classes --

class AirVPNBaseEntity(CoordinatorEntity):
    def __init__(self, coordinator, device_id, entity_key, name_suffix, icon, device_name_prefix):
        super().__init__(coordinator)
        
        self._entity_key = entity_key

        self._attr_unique_id = f"{device_id}_{entity_key}"
        self._attr_name = f"{device_name_prefix} {name_suffix}"
        self._attr_icon = icon
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": device_name_prefix,
            "manufacturer": "AirVPN",
        }

class AirVPNBaseSensor(AirVPNBaseEntity, SensorEntity):    
    def __init__(self, coordinator, device_id, entity_key, name_suffix, unit, icon, device_name_prefix="AirVPN", device_class=None):
        super().__init__(coordinator, device_id, entity_key, name_suffix, icon, device_name_prefix)
        self._attr_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = SensorStateClass.MEASUREMENT
        
    @property
    def state(self):
        data = self._get_data()
        return data.get(self._entity_key) if data else None


class AirVPNUserSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, name, key, device_id, device_name, unit=None, icon=None, device_class=None, state_class=None):
        super().__init__(coordinator)
        self._name = name
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

class AirVPNUserBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, name, key, device_id, device_name, icon=None):
        super().__init__(coordinator)
        self._name = name
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

class AirVPNDeviceSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device_data, name, key, icon, device_id, device_name, unit=None, device_class=None, state_class=None):
        super().__init__(coordinator)
        self._device_data = device_data
        self._name = name
        self._key = key
        self._attr_unique_id = f"airvpn_device_{device_id}_{key}"
        self._attr_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": f"AirVPN Device ({device_name})",
            "manufacturer": "AirVPN",
        }

    @property
    def name(self):
        return self._name
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._device_data.get(self._key)

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

class AirVPNSessionSensor(AirVPNBaseSensor):
    def __init__(self, coordinator, device_id, device_name, *args, **kwargs):
        self._device_name = device_name
        super().__init__(coordinator, device_id, *args, device_name_prefix=f"AirVPN Device ({device_name})", **kwargs)

    def _get_data(self):
        for session in self.coordinator.data.get("sessions", []):
            if session.get("device_name") == self._device_name:
                return session
        return None