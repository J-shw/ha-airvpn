from datetime import timedelta
import asyncio
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AirVPNApi
from .types import AirVPNData, UserInfoResponse, DeviceInfoResponse

_LOGGER = logging.getLogger(__name__)

class AirVPNUpdateCoordinator(DataUpdateCoordinator[AirVPNData]):
    """Class to manage fetching AirVPN data."""

    def __init__(self, hass: HomeAssistant, api: AirVPNApi) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="AirVPN",
            update_interval=timedelta(seconds=300),
        )
        self.api = api

    async def _async_update_data(self) -> AirVPNData:
        """Update data via API."""
        try:
            user_info, device_info = await asyncio.gather(
                self.api.get_user_info(),
                self.api.get_devices()
            )

            if user_info.get("result") != "ok":
                raise UpdateFailed(f"User API error: {user_info.get('result')}")
            
            if device_info.get("result") != "ok":
                raise UpdateFailed(f"Device API error: {device_info.get('result')}")

            return {
                "user": user_info["user"],
                "sessions": user_info.get("sessions", []),
                "devices": device_info.get("devices", []),
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")