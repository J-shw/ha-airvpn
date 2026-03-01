from typing import TypedDict, List, Literal, Union

# Now I don't actually know all the literals yet... But I am hoping to add them to this as I do.
VPNAttemptMessage = Union[Literal["OK"], str]
VPNStatus = Union[Literal["ready"], str]
ResponseResult = Union[Literal["ok"], str]

class AirVPNUser(TypedDict):
    login: str
    """The username of the user."""
    premium: bool
    """Whether the user has premium access."""
    expiration_days: int
    """The number of days until the user's premium expires."""
    posts: str
    """The number of posts the user has made."""
    last_post: str
    """The last post the user made? Not sure what this is."""
    register_unix: int
    """The unix timestamp of when the user registered."""
    register_date: str
    """The date the user registered."""
    expiration_unix: int
    """The unix timestamp of when the user's premium expires."""
    expiration_date: str
    """The date the user's premium expires."""
    last_visit_unix: int
    """The unix timestamp of when the user last visited."""
    last_visit_date: str
    """The date the user last visited."""
    credits: int
    """The number of credits the user has."""
    last_attempt_unix: int
    """The unix timestamp of when the user last attempted to connect."""
    last_attempt_date: str
    """The date the user last attempted to connect."""
    credit: List[str]
    """Not sure what this is.."""
    connected: bool
    """Whether the user is currently connected."""

class AirVPNSession(TypedDict):
    device_name: str
    """The name of the device."""
    device_description: str
    """The description of the device."""
    vpn_ip: str
    """The IP address of the VPN connection."""
    vpn_ipv4: str
    """The IPv4 address of the VPN connection."""
    vpn_ipv6: str
    """The IPv6 address of the VPN connection."""
    exit_ip: str
    """The exit IP address of the VPN connection."""
    exit_ipv4: str
    """The exit IPv4 address of the VPN connection."""
    exit_ipv6: str
    """The exit IPv6 address of the VPN connection."""
    entry_ip: str
    """The entry IP address of the VPN connection."""
    entry_ipv4: str
    """The entry IPv4 address of the VPN connection."""
    entry_ipv6: str
    """The entry IPv6 address of the VPN connection."""
    server_name: str
    """The name of the server."""
    server_country: str
    """The country of the server."""
    server_country_code: str
    """The country code of the server."""
    server_continent: str
    """The continent of the server."""
    server_location: str
    """The location of the server."""
    server_bw: int
    """The bandwidth of the server."""
    bytes_read: int
    """The number of bytes read."""
    bytes_write: int
    """The number of bytes written."""
    connected_since_date: str
    """The date the user connected."""
    connected_since_unix: int
    """The unix timestamp of when the user connected."""
    speed_read: int
    """The download speed."""
    speed_write: int
    """The upload speed."""

class AirVPNDevice(TypedDict):
    id: str
    """The ID of the device."""
    name: str
    """The name of the device."""
    description: str
    """The description of the device."""
    version: str
    """The version of encryption."""
    renew_first_unix: int
    """The unix timestamp of when the device will renew."""
    renew_first_date: str
    """The date the device will renew."""
    renew_last_unix: int
    """The unix timestamp of when the device last renewed."""
    renew_last_date: str
    """The date the device last renewed."""
    renew_counter: int
    """The number of times the device has renewed?"""
    wireguard_public_key: str
    """The public key of the device."""
    wireguard_ipv4: str
    """The IPv4 address of the device."""
    wireguard_ipv6: str
    """The IPv6 address of the device."""
    vpn_last_from_unix: int
    """The unix timestamp of when the device last connected."""
    vpn_last_from_date: str
    """The date the device last connected."""
    vpn_last_to_unix: int
    """The unix timestamp of when the device last disconnected."""
    vpn_last_to_date: str
    """The date the device last disconnected."""
    vpn_attempt_unix: int
    """The unix timestamp of when the device last attempted to connect."""
    vpn_attempt_date: str
    """The date the device last attempted to connect."""
    vpn_attempt_message: VPNAttemptMessage
    """The message of the last attempt."""
    status: VPNStatus
    """The status of the device."""

class GeoSmall(TypedDict):
    """The small geo data"""
    code: str
    """The country code."""
    name: str
    """The country name."""

class GeoAdditional(TypedDict):
    ts: int
    """The timestamp of the geo data."""
    as_number: int
    """The AS number."""
    isp_name: str
    """The ISP name."""
    country_code: str
    """The country code."""
    country_name: str
    """The country name."""
    region_code: str
    """The region code."""
    region_name: str
    """The region name."""
    continent_code: str
    """The continent code."""
    continent_name: str
    """The continent name."""
    city_name: str
    """The city name."""
    postal_code: str | None
    """The zip code."""
    postal_confidence: int | None
    """The confidence of the post code."""
    latitude: float
    """The latitude of the location."""
    longitude: float
    """The longitude of the location."""
    accuracy_radius: int
    """The accuracy of the location."""
    timezone: str
    """The timezone of the location."""
    metro_code: str | None
    """The metro code."""
    code: str
    """The country code again?"""
    name: str
    """The country name again?"""
    notes: str
    """Just some notes about guarantees"""


class UserInfoResponse(TypedDict):
    """The response from the user info endpoint."""

    user: AirVPNUser
    """The user information."""
    sessions: List[AirVPNSession]
    """The list of sessions."""
    connection: dict
    """Not sure what this is... It seems to shown a single connection even though I have multiple?"""
    result: ResponseResult
    """The result of the request. `ok` seems to be the good response."""

class DeviceInfoResponse(TypedDict):
    """The response from the device info endpoint."""

    action: str
    """The action taken."""
    devices: List[AirVPNDevice]
    """The list of devices."""
    result: ResponseResult
    """`ok` seems to be the good response."""

class WhatsMyIpResponse(TypedDict):
    """The response from the whatsmyip endpoint."""

    ip: str
    """The IP address."""
    ipv4: bool
    """Whether the IP is IPv4."""
    ipv6: bool
    """Whether the IP is IPv6."""
    airvpn: bool
    """Whether the IP is from AirVPN."""
    geo: GeoSmall
    """Geo info"""
    geo_additional: GeoAdditional
    """Additional geo info"""
    result: ResponseResult
    """`ok` seems to be the good response."""


class AirVPNData(TypedDict):
    """The final merged data object used by the Coordinator."""

    user: AirVPNUser
    """The user information."""
    devices: List[AirVPNDevice]
    """The list of devices."""
    sessions: List[AirVPNSession]
    """The list of sessions."""
    ip_data: WhatsMyIpResponse
    """The IP data."""