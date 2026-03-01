import asyncio
from typing import Any
import aiohttp
from .types import UserInfoResponse, DeviceInfoResponse

class AirVPNApi:
    """Client to interact with the AirVPN API."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession) -> None:
        self._api_key = api_key
        self._session = session
        self._base_url = "https://airvpn.org/api"

    async def _get_request(self, endpoint: str) -> Any:
        """Internal helper to make GET requests."""
        url = f"{self._base_url}/{endpoint}/?key={self._api_key}"
        try:
            async with self._session.get(url, timeout=10) as response:
                response.raise_for_status()
                return await response.json()
        except asyncio.TimeoutError:
            raise Exception("Timeout connecting to AirVPN API")
        except aiohttp.ClientError as err:
            raise Exception(f"Communication error: {err}")

    async def get_user_info(self) -> UserInfoResponse:
        """Get user account and session data."""
        return await self._get_request("userinfo")

    async def get_devices(self) -> DeviceInfoResponse:
        """Get registered devices data."""
        return await self._get_request("devices")