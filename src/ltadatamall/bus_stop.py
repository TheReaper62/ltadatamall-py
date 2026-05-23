from typing import TypedDict, Unpack

from .base import BaseModel

__all__ = [
    "BusStop",
]


class BusStopPayload(TypedDict, total=False):
    BusStopCode: str | int
    RoadName: str
    Description: str
    Latitude: str | float
    Longitude: str | float


class BusStop:
    """Represents a physical bus stop containing metadata and geographic location coordinates.

    This class ingests raw API response payloads via keyword arguments, normalizes
    codes into human-readable strings, and forces coordinate parameters into float precision.
    """

    def __init__(self, **kwargs: Unpack[BusStopPayload]) -> None:
        self.bus_stop_code: str = str(kwargs.get("BusStopCode", "Not Available"))
        self.road_name: str = kwargs.get("RoadName", "Not Available")
        self.description: str = kwargs.get("Description", "Not Available")

        self.latitude: float = float(kwargs.get("Latitude", 0.0))
        self.longitude: float = float(kwargs.get("Longitude", 0.0))
