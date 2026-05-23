from typing import TypedDict, Unpack, Any

from .base import BaseModel

__all__ = [
    "TrainServiceAlert",
    "TrainServiceAlertManager",
]


class TrainServiceAlertPayload(TypedDict, total=False):
    Status: str | int
    Line: str
    Direction: str
    Stations: str
    FreePublicBus: str
    FreeMRTShuttle: str
    MRTShuttleDirection: str
    Message: str


class TrainServiceAlert:
    """Model representing an active transit service disruption alert on the rail network."""

    def __init__(self, **kwargs: Unpack[TrainServiceAlertPayload]) -> None:
        self.status: str = str(kwargs.get("Status", "Not Available"))
        self.line: str = kwargs.get("Line", "Not Available")
        self.direction: str = kwargs.get("Direction", "Not Available")
        self.mrt_shuttle_direction: str = kwargs.get(
            "MRTShuttleDirection", "Not Available"
        )
        self.message: str = kwargs.get("Message", "No Message")

        self.stations: list[str] | str = self._parse_comma_string(
            kwargs.get("Stations")
        )
        self.free_public_bus: list[str] | str = self._parse_comma_string(
            kwargs.get("FreePublicBus")
        )
        self.free_mrt_shuttle: list[str] | str = self._parse_comma_string(
            kwargs.get("FreeMRTShuttle")
        )

    def _parse_comma_string(self, raw_value: Any) -> list[str] | str:
        """Safely parses comma-separated API string parameters into clean lists."""
        if raw_value is None or str(raw_value).strip() == "":
            return "Not Available"
        return [item.strip() for item in str(raw_value).split(",") if item.strip()]


class TrainServiceAlertManager(BaseModel):
    """Orchestrates API bindings to monitor live rail transit network alert data streams."""

    def get_alerts(self) -> list[TrainServiceAlert]:
        """Fetches active train service disruption alerts.

        Returns:
            A list containing active TrainServiceAlert status tracking frameworks.
        """
        response = self.send("TrainServiceAlerts")
        value_list = response.get("value")

        if not isinstance(value_list, list):
            raise ValueError(
                "LTA DataMall API did not yield a valid data list layout for TrainServiceAlerts."
            )

        return [TrainServiceAlert(**alert) for alert in value_list]

    async def async_get_alerts(self) -> list[TrainServiceAlert]:
        """Asynchronously fetches active train service disruption alerts."""
        response = await self.async_send("TrainServiceAlerts", params=None, json=None)
        value_list = response.get("value")

        if not isinstance(value_list, list):
            raise ValueError(
                "LTA DataMall API did not yield a valid data list layout for TrainServiceAlerts."
            )

        return [TrainServiceAlert(**alert) for alert in value_list]
