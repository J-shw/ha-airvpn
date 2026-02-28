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


class UserInfoResponse(TypedDict):
    user: AirVPNUser
    """The user information."""
    sessions: List[AirVPNSession]
    """The list of sessions."""
    connection: dict
    """Not sure what this is... It seems to shown a single connection even though I have multiple?"""
    result: ResponseResult
    """The result of the request. `ok` seems to be the good response."""

class DeviceInfoResponse(TypedDict):
    action: str
    """The action taken."""
    devices: List[AirVPNDevice]
    """The list of devices."""
    result: ResponseResult
    """`ok` seems to be the good response."""
