from typing import TypedDict, Unpack

from .base import BaseModel

__all__ = [
    "BusService",
]


class BusServicePayload(TypedDict, total=False):
    ServiceNo: str
    Operator: str
    Direction: int | str
    Category: str
    OriginCode: str
    DestinationCode: str
    AM_Peak_Freq: str
    AM_Offpeak_Freq: str
    PM_Peak_Freq: str
    PM_Offpeak_Freq: str
    LoopDesc: str


class BusService:
    """Model representing metadata for a specific bus route service configuration.

    This class extracts the operating schedule frequency, service loop descriptors,
    and handling agency constraints from raw LTA data data streams.
    """

    def __init__(self, **kwargs: Unpack[BusServicePayload]) -> None:
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
        self.category: str | None = kwargs.get("Category", None)
        self.origin_code: str | None = kwargs.get("OriginCode", None)
        self.destination_code: str | None = kwargs.get("DestinationCode", None)
        self.am_peak_freq: str | None = kwargs.get("AM_Peak_Freq", None)
        self.am_offpeak_freq: str | None = kwargs.get("AM_Offpeak_Freq", None)
        self.pm_peak_freq: str | None = kwargs.get("PM_Peak_Freq", None)
        self.pm_offpeak_freq: str | None = kwargs.get("PM_Offpeak_Freq", None)
        self.loop_desc: str | None = kwargs.get("LoopDesc", None)
