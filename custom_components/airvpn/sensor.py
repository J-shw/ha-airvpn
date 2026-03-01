import logging
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import (
    UnitOfInformation,
    UnitOfDataRate,
    UnitOfTime,
)

from .const import DOMAIN
from .coordinator import AirVPNUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, 
    entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up AirVPN sensors."""
    coordinator: AirVPNUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    user = coordinator.data["user"]
    entities = []

    # User data

    entities.extend([
        AirVPNUserSensor(coordinator, "expiration_days", "Expiration Days", "mdi:calendar", unit=UnitOfTime.DAYS),
        AirVPNUserSensor(coordinator, "credits", "Credits", "mdi:numeric"),
        AirVPNUserBinarySensor(coordinator, "connected", "Connection Status", "mdi:vpn", BinarySensorDeviceClass.CONNECTIVITY),
        AirVPNUserBinarySensor(coordinator, "premium", "Premium Status", "mdi:crown"),
    ])

    # Device data

    for device in coordinator.data.get("devices", []):
        d_id, d_name = device["id"], device["name"]
        
        entities.extend([
            AirVPNDeviceSensor(coordinator, d_id, d_name, "status", "Status", "mdi:list-status"),
            AirVPNDeviceSensor(coordinator, d_id, d_name, "vpn_attempt_message", "Last Attempt Message", "mdi:message-text-outline"),
            AirVPNDeviceSensor(coordinator, d_id, d_name, "vpn_last_from_date", "Last Connected", "mdi:clock-out"),
        ])

    for session in coordinator.data.get("sessions", []):
        s_name = session["device_name"]
        # Find ID to group with the Device Registry entry
        d_id = next((d["id"] for d in coordinator.data["devices"] if d["name"] == s_name), s_name)

        entities.extend([
            AirVPNSessionSensor(coordinator, d_id, s_name, "server_name", "Connected Server", "mdi:server"),
            AirVPNSessionSensor(coordinator, d_id, s_name, "exit_ip", "Exit IP", "mdi:ip-network"),
            
            # Data Rates
            AirVPNSessionSensor(coordinator, d_id, s_name, "speed_read", "Download Speed", "mdi:download", unit=UnitOfDataRate.BYTES_PER_SECOND, device_class=SensorDeviceClass.DATA_RATE, state_class=SensorStateClass.MEASUREMENT),
            AirVPNSessionSensor(coordinator, d_id, s_name, "speed_write", "Upload Speed", "mdi:upload", unit=UnitOfDataRate.BYTES_PER_SECOND, device_class=SensorDeviceClass.DATA_RATE, state_class=SensorStateClass.MEASUREMENT),
            
            # Data Totals
            AirVPNSessionSensor(coordinator, d_id, s_name, "bytes_read", "Total Downloaded", "mdi:download-outline", unit=UnitOfInformation.BYTES, device_class=SensorDeviceClass.DATA_SIZE, state_class=SensorStateClass.TOTAL_INCREASING),
            AirVPNSessionSensor(coordinator, d_id, s_name, "bytes_write", "Total Uploaded", "mdi:upload-outline", unit=UnitOfInformation.BYTES, device_class=SensorDeviceClass.DATA_SIZE, state_class=SensorStateClass.TOTAL_INCREASING),
        ])

    async_add_entities(entities)

# -- Base Class --

class AirVPNEntity(CoordinatorEntity[AirVPNUpdateCoordinator]):
    """Base class for all AirVPN entities."""
    _attr_has_entity_name = True

    def __init__(self, coordinator, unique_id, name, device_id, device_name, icon=None):
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{unique_id}"
        self._attr_name = name
        self._attr_icon = icon
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": device_name,
            "manufacturer": "AirVPN",
        }
# -- User Entities --

class AirVPNUserSensor(AirVPNEntity, SensorEntity):
    """Sensor for User account data."""
    def __init__(self, coordinator, key, name, icon, unit=None, device_class=None, state_class=None):
        login = coordinator.data["user"]["login"]
        super().__init__(coordinator, f"user_{login}_{key}", name, f"user_{login}", f"AirVPN ({login})", icon)
        self._key = key
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def native_value(self):
        return self.coordinator.data["user"].get(self._key)

class AirVPNUserBinarySensor(AirVPNEntity, BinarySensorEntity):
    """Binary Sensor for User account states (Connected, Premium)."""
    def __init__(self, coordinator, key, name, icon, device_class=None):
        login = coordinator.data["user"]["login"]
        super().__init__(coordinator, f"user_{login}_{key}", name, f"user_{login}", f"AirVPN ({login})", icon)
        self._key = key
        self._attr_device_class = device_class

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data["user"].get(self._key))

# -- Device Entities --

class AirVPNDeviceSensor(AirVPNEntity, SensorEntity):
    """Sensor for static Device data (Status, Last Attempt)."""
    def __init__(self, coordinator, device_id, device_name, key, name, icon, unit=None, device_class=None):
        super().__init__(coordinator, f"dev_{device_id}_{key}", name, device_id, f"Device: {device_name}", icon)
        self._device_id = device_id
        self._key = key
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class

    @property
    def native_value(self):
        device = next((d for d in self.coordinator.data["devices"] if d["id"] == self._device_id), None)
        return device.get(self._key) if device else None

# -- Session Entities --

class AirVPNSessionSensor(AirVPNEntity, SensorEntity):
    """Sensor for live Session data (Speed, IP, Server)."""
    def __init__(
        self, 
        coordinator: AirVPNUpdateCoordinator, 
        device_id: str, 
        device_name: str, 
        key: str, 
        name: str, 
        icon: str,
        unit: str | None = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None
    ) -> None:
        super().__init__(coordinator, f"sess_{device_name}_{key}", name, device_id, f"Device: {device_name}", icon)
        self._device_name = device_name
        self._key = key
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def native_value(self):
        session = next((s for s in self.coordinator.data["sessions"] if s["device_name"] == self._device_name), None)
        return session.get(self._key) if session else None