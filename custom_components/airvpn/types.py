from typing import TypedDict, List, Optional

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

class UserInfoResponse(TypedDict):
    user: AirVPNUser
    sessions: List[dict]
