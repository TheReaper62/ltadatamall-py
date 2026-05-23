from typing import TypedDict, Unpack

from .base import BaseModel

__all__ = [
    "BusRoute",
]


class BusRoutePayload(TypedDict, total=False):
    ServiceNo: str
    Operator: str
    Direction: int | str
    StopSequence: int | str
    BusStopCode: str | int
    Distance: float | str
    WD_FirstBus: str
    WD_LastBus: str
    SAT_FirstBus: str
    SAT_LastBus: str
    SUN_FirstBus: str
    SUN_LastBus: str


class BusRoute:
    """Model representing a sequential bus route stop entry.

    This class handles specific schedule timings, distance metrics, and sequencing
    indices for unique service routes across Singapore's transit network.
    """

    def __init__(self, **kwargs: Unpack[BusRoutePayload]) -> None:
        operator_map: dict[str, str] = {
            "SBST": "SBS Transit",
            "SMRT": "SMRT Corporation",
            "TTS": "Tower Transit Singapore",
            "GAS": "Go Ahead Singapore",
        }

        self.service_no: str | None = kwargs.get("ServiceNo", None)

        self.operator: str = operator_map.get(
            kwargs.get("Operator", ""), "Not Available"
        )

        self.direction: int | None = (
            int(kwargs["Direction"]) if kwargs.get("Direction") is not None else None
        )
        self.stop_sequence: int | None = (
            int(kwargs["StopSequence"])
            if kwargs.get("StopSequence") is not None
            else None
        )

        self.bus_stop_code: str | None = (
            str(kwargs["BusStopCode"])
            if kwargs.get("BusStopCode") is not None
            else None
        )

        self.distance: float | None = (
            float(kwargs["Distance"]) if kwargs.get("Distance") is not None else None
        )

        # Timeline schedule fields
        self.wd_firstbus: str | None = kwargs.get("WD_FirstBus", None)
        self.wd_lastbus: str | None = kwargs.get("WD_LastBus", None)
        self.sat_firstbus: str | None = kwargs.get("SAT_FirstBus", None)
        self.sat_lastbus: str | None = kwargs.get("SAT_LastBus", None)
        self.sun_firstbus: str | None = kwargs.get("SUN_FirstBus", None)
        self.sun_lastbus: str | None = kwargs.get("SUN_LastBus", None)
