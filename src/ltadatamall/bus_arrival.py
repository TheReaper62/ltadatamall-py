from typing import Optional, Unpack, TypedDict
from datetime import datetime
import zoneinfo

__all__ = [
    'NextBus',
    'BusArrivalService',
]


class NextBusPayload(TypedDict, total=False):
    OriginCode: str
    DestinationCode: str
    EstimatedArrival: str
    Latitude: str
    Longitude: str
    VisitNumber: str
    Load: str
    Feature: str
    Type: str


class NextBus:
    """
    Represents an arriving bus service with parsed telemetry and capacity data.

    This class ingests raw API response payloads via keyword arguments, normalizes 
    codes into human-readable strings, and parses arrival timestamps into timezone-aware 
    datetime objects.
    """

    def __init__(self, **kwargs: Unpack[NextBusPayload]) -> None:
        load_map = {
            "SEA": "Seats Available",
            "SDA": "Standing Available",
            "LSD": "Limited Standing",
        }
        type_map = {"SD": "Single Decker", "DD": "Double Decker", "BD": "Bendy"}

        self.origin_code = kwargs.get("OriginCode", "Not Available")
        self.destination_code = kwargs.get("DestinationCode", "Not Available")

        self.estimated_arrival = (
            datetime.strptime(kwargs["EstimatedArrival"], r"%Y-%m-%dT%H:%M:%S%z")
            if kwargs.get("EstimatedArrival", "") != ""
            else "No Estimated Time"
        )
        self.latitude = kwargs.get("Latitude", 0.0)
        self.longitude = kwargs.get("Longitude", 0.0)

        self.visit_number = (
            int(kwargs["VisitNumber"])
            if kwargs.get("VisitNumber", "") != ""
            else "Not Available"
        )
        self.load = load_map.get(kwargs.get("Load", None), "Not Available")
        self.feature = (
            "Not Wheel-chair Accessible"
            if kwargs.get("Feature", "") == ""
            else "Wheel-chair Accessible"
        )
        self.type = type_map.get(kwargs.get("Type"), "Not Available")


class BusArrivalServicePayload(TypedDict, total=False):
    ServiceNo: str
    Operator: str
    NextBus: NextBusPayload
    NextBus2: NextBusPayload
    NextBus3: NextBusPayload


class BusArrivalService:
    """Model representing arrival information for a specific bus service at a bus stop.

    This class parses metadata for a distinct transit route code and instantiates
    the upcoming three scheduled arrival vehicle telemetry profiles.
    """

    def __init__(self, **kwargs: Unpack[BusArrivalServicePayload]) -> None:
        operator_map: dict[str, str] = {
            "SBST": "SBS Transit",
            "SMRT": "SMRT Corporation",
            "TTS": "Tower Transit Singapore",
            "GAS": "Go Ahead Singapore",
        }

        # Handle explicit type coercions safely
        raw_service_no = kwargs.get("ServiceNo")
        self.service_no: Optional[int] = (
            int(raw_service_no) if raw_service_no is not None else None
        )

        self.operator: str = operator_map.get(
            kwargs.get("Operator", ""), "Not Available"
        )

        # 2. Extract nested structures and instantiate NextBus objects cleanly
        self.next_1: NextBus = NextBus(**kwargs.get("NextBus", {}))
        self.next_2: NextBus = NextBus(**kwargs.get("NextBus2", {}))
        self.next_3: NextBus = NextBus(**kwargs.get("NextBus3", {}))

        self.secs_to_arrival: Optional[int] = None
        self._calculate_seconds_to_arrival()

    def _calculate_seconds_to_arrival(self) -> None:
        """Calculates time delta between now and next_1 arrival in seconds."""
        if (
            isinstance(self.next_1.estimated_arrival, str)
            or self.next_1.estimated_arrival == "No Estimated Time"
        ):
            self.secs_to_arrival = None
            return

        sg_tz = zoneinfo.ZoneInfo("Asia/Singapore")
        now_sg = datetime.now(sg_tz)

        time_delta = self.next_1.estimated_arrival - now_sg
        total_seconds = int(time_delta.total_seconds())

        self.secs_to_arrival = total_seconds
