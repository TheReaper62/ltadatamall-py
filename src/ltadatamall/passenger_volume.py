from .base import BaseModel

__all__ = [
    "PassengerVolume",
]


class PassengerVolume(BaseModel):
    """Orchestrates LTA DataMall API bindings for monthly passenger volume downloads.

    Provides dynamic downloadable asset links tracking transit volume matrices
    across bus stops, train lines, and origin-destination nodes.
    """

    # 1. Passenger Volume By Bus Stop
    def pv_bus_stop(self, date: str | None = None) -> str:
        """Fetches the download URL link for passenger volumes by bus stops.

        Args:
            date: Targeted month in YYYYMM format (e.g., "202603"). Defaults
                to the latest available month data from LTA if omitted.
        """
        params = {"Date": date} if date else None
        response = self.send("PV/Bus", params=params)
        return self._extract_download_link(response, "PV/Bus")

    async def async_pv_bus_stop(self, date: str | None = None) -> str:
        """Asynchronously fetches the download URL link for passenger volumes by bus stops."""
        params = {"Date": date} if date else None
        response = await self.async_send("PV/Bus", params=params, json=None)
        return self._extract_download_link(response, "PV/Bus")

    # 2. Passenger Volume By Origin-Destination Bus Stops
    def pv_od_bus_stop(self, date: str | None = None) -> str:
        """Fetches the download URL link for origin-destination passenger volumes by bus stops."""
        params = {"Date": date} if date else None
        response = self.send("PV/ODBus", params=params)
        return self._extract_download_link(response, "PV/ODBus")

    async def async_pv_od_bus_stop(self, date: str | None = None) -> str:
        """Asynchronously fetches the download URL link for origin-destination passenger volumes by bus stops."""
        params = {"Date": date} if date else None
        response = await self.async_send("PV/ODBus", params=params, json=None)
        return self._extract_download_link(response, "PV/ODBus")

    # 3. Passenger Volume By Origin-Destination Train Stations
    def pv_od_train_destination(self, date: str | None = None) -> str:
        """Fetches the download URL link for origin-destination passenger volumes by train stations."""
        params = {"Date": date} if date else None
        response = self.send("PV/ODTrain", params=params)
        return self._extract_download_link(response, "PV/ODTrain")

    async def async_pv_od_train_destination(self, date: str | None = None) -> str:
        """Asynchronously fetches the download URL link for origin-destination passenger volumes by train stations."""
        params = {"Date": date} if date else None
        response = await self.async_send("PV/ODTrain", params=params, json=None)
        return self._extract_download_link(response, "PV/ODTrain")

    # 4. Passenger Volume By Train Stations
    def pv_train_station(self, date: str | None = None) -> str:
        """Fetches the download URL link for passenger volumes by individual train stations."""
        params = {"Date": date} if date else None
        response = self.send("PV/Train", params=params)
        return self._extract_download_link(response, "PV/Train")

    async def async_pv_train_station(self, date: str | None = None) -> str:
        """Asynchronously fetches the download URL link for passenger volumes by individual train stations."""
        params = {"Date": date} if date else None
        response = await self.async_send("PV/Train", params=params, json=None)
        return self._extract_download_link(response, "PV/Train")

    def _extract_download_link(self, response: dict[str, any], endpoint: str) -> str:
        """Safely extracts the nested download URL link from LTA's response payload array wrapper."""
        value_list = response.get("value")

        if isinstance(value_list, list) and len(value_list) > 0:
            link = value_list[0].get("Link")
            if link:
                return str(link)

        raise ValueError(
            f"LTA DataMall API did not yield a valid download link structural layout for endpoint: '{endpoint}'"
        )
