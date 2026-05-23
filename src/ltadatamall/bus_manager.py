from typing import Any

from .base import BaseModel

from .bus_stop import BusStop
from .bus_service import BusService
from .bus_route import BusRoute
from .bus_arrival import BusArrivalService

__all__ = (
    'BusManager',
)


class BusManager(BaseModel):
    """Orchestrates API for tracking bus routes and operational status profiles."""

    def get_bus_arrival(
        self,
        bus_stop_code: str | int | BusStop,
        *,
        service_no: str | int | None = None,
    ) -> list[BusArrivalService]:
        """Fetches real-time bus arrival timelines for a specific bus stop code.

        Args:
            bus_stop_code: The 5-digit unique transit stop code or a BusStop instance.
            service_no: Optional specific transit service route number to filter results.

        Returns:
            A list containing active BusArrivalService status track records.
        """
        params = self._prepare_arrival_params(bus_stop_code, service_no)
        response = self.send("v3/BusArrival", params=params)

        services = response.get("Services")
        if isinstance(services, list):
            return [BusArrivalService(**item) for item in services]

        raise ValueError(
            f"LTA DataMall API did not yield any service items for parameters: {params}"
        )

    async def async_get_bus_arrival(
        self,
        bus_stop_code: str | int | BusStop,
        *,
        service_no: str | int | None = None,
    ) -> list[BusArrivalService]:
        """Asynchronously fetches real-time bus arrival timelines for a specific bus stop code."""
        params = self._prepare_arrival_params(bus_stop_code, service_no)

        response = await self.async_send("v3/BusArrival", params=params, json=None)

        services = response.get("Services")
        if isinstance(services, list):
            return [BusArrivalService(**item) for item in services]

        raise ValueError(
            "LTA DataMall API did not yield any service items for the specified parameters."
        )

    def _prepare_arrival_params(
        self, bus_stop_code: str | int | BusStop, service_no: str | int | None
    ) -> dict[str, Any]:
        """Internal helper logic block designed to standardise all codes to strings."""
        code = (
            bus_stop_code.bus_stop_code
            if isinstance(bus_stop_code, BusStop)
            else str(bus_stop_code)
        )

        params: dict[str, Any] = {"BusStopCode": code}
        if service_no is not None:
            params["ServiceNo"] = str(service_no)

        return params

    def get_services(
        self,
        services: list[str | int] | None = None
    ) -> list[BusService]:
        """Fetches comprehensive metadata for active bus routes.

        Args:
            services: Optional explicit list of route numbers to filter. 
                If None, all available services are returned.
        """
        response = self.send("BusServices")
        value_list = response.get("value")

        if not isinstance(value_list, list):
            raise ValueError(
                "LTA DataMall API did not yield a valid data list layout for BusServices."
            )

        if services is None:
            return [BusService(**item) for item in value_list]

        # Optimization: Use a hashed set lookup instead of rebuilding a map list inside a loop
        target_services = {str(s) for s in services}
        return [
            BusService(**item)
            for item in value_list
            if str(item.get("ServiceNo")) in target_services
        ]

    async def async_get_services(
        self,
        services: list[str | int] | None = None
    ) -> list[BusService]:
        """Asynchronously fetches comprehensive metadata for active bus routes."""
        response = await self.async_send("BusServices", params=None, json=None)
        value_list = response.get("value")

        if not isinstance(value_list, list):
            raise ValueError(
                "LTA DataMall API did not yield a valid data list layout for BusServices."
            )

        if services is None:
            return [BusService(**item) for item in value_list]

        target_services = {str(s) for s in services}
        return [
            BusService(**item)
            for item in value_list
            if str(item.get("ServiceNo")) in target_services
        ]

    def get_all_services(self) -> list[BusService]:
        """Fetches all active bus service records by automatically paginating
        through the 500-record payload threshold constraints.
        """
        services: list[BusService] = []
        skip_offset = 0

        while True:
            response = self.send("BusServices", params={"$skip": skip_offset})
            records = response.get("value")

            if not isinstance(records, list) or not records:
                if skip_offset == 0:
                    raise ValueError(
                        "LTA DataMall API returned an empty or invalid BusServices payload."
                    )
                break
            services.extend([BusService(**item) for item in records])

            if len(records) < 500:
                break
            skip_offset += 500
        return services

    async def async_get_all_services(self) -> list[BusService]:
        """Asynchronously fetches all active bus service records by handling pagination."""
        services: list[BusService] = []
        skip_offset = 0

        while True:
            response = await self.async_send(
                "BusServices", params={"$skip": skip_offset}, json=None
            )
            records = response.get("value")

            if not isinstance(records, list) or not records:
                if skip_offset == 0:
                    raise ValueError(
                        "LTA DataMall API returned an empty or invalid BusServices payload."
                    )
                break
            services.extend([BusService(**item) for item in records])

            if len(records) < 500:
                break
            skip_offset += 500
        return services

    def get_routes(self, **filters: Any) -> list[BusRoute]:
        """Fetches a single page of bus route data and applies filters.

        Args:
            **filters: Optional keyword arguments matching model attributes 
                (e.g., service_no="190", bus_stop_code="65009").
        """
        # FIX: Standardized endpoint path from singular 'BusRoute' to plural 'BusRoutes'
        response = self.send("BusRoutes")
        value_list = response.get("value")

        if not isinstance(value_list, list):
            raise ValueError("LTA DataMall API did not yield a valid data list layout for BusRoutes.")

        if not filters:
            return [BusRoute(**item) for item in value_list]

        # Map Python snake_case filters to LTA PascalCase keys
        pascal_filters = self._normalize_filters(filters)

        return [
            BusRoute(**item)
            for item in value_list
            if all(item.get(k) == v for k, v in pascal_filters.items())
        ]

    async def async_get_routes(self, **filters: Any) -> list[BusRoute]:
        """Asynchronously fetches a single page of bus route data and applies filters."""
        # FIX 1: Added await keyword
        # FIX 2: Corrected endpoint from singular to plural 'BusRoutes'
        # FIX 3: Supplied json=None keyword matching BaseModel signature
        response = await self.async_send("BusRoutes", params=None, json=None)
        value_list = response.get("value")

        if not isinstance(value_list, list):
            raise ValueError("LTA DataMall API did not yield a valid data list layout for BusRoutes.")

        if not filters:
            return [BusRoute(**item) for item in value_list]

        pascal_filters = self._normalize_filters(filters)

        return [
            BusRoute(**item)
            for item in value_list
            if all(item.get(k) == v for k, v in pascal_filters.items())
        ]

    def get_all_routes(self) -> list[BusRoute]:
        """Fetches all bus route records by automatically handling the 500-record pagination limit."""
        routes: list[BusRoute] = []
        skip_offset = 0

        while True:
            response = self.send("BusRoutes", params={"$skip": skip_offset})
            records = response.get("value")
            if not isinstance(records, list) or not records:
                if skip_offset == 0:
                    raise ValueError("LTA DataMall API returned an empty or invalid BusRoutes payload.")
                break
            routes.extend([BusRoute(**item) for item in records])

            if len(records) < 500:
                break
            skip_offset += 500
        return routes

    async def async_get_all_routes(self) -> list[BusRoute]:
        """Asynchronously fetches all bus route records by handling pagination constraints cleanly."""
        routes: list[BusRoute] = []
        skip_offset = 0

        while True:
            response = await self.async_send("BusRoutes", params={"$skip": skip_offset}, json=None)
            records = response.get("value")
            if not isinstance(records, list) or not records:
                if skip_offset == 0:
                    raise ValueError("LTA DataMall API returned an empty or invalid BusRoutes payload.")
                break
            routes.extend([BusRoute(**item) for item in records])

            if len(records) < 500:
                break
            skip_offset += 500
        return routes

    def _normalize_filters(self, filters: dict[str, Any]) -> dict[str, Any]:
        """Helper to map common snake_case filter keys to LTA data field shapes."""
        mapping = {
            "service_no": "ServiceNo",
            "operator": "Operator",
            "direction": "Direction",
            "stop_sequence": "StopSequence",
            "bus_stop_code": "BusStopCode",
        }
        return {mapping.get(k, k): v for k, v in filters.items()}

    def get_stops(self, bus_stop_codes: str | int | list[str | int]) -> list[BusStop] | BusStop | None:
        """Retrieves targeted bus stop configurations from the complete database.

        Args:
            bus_stop_codes: A single stop code (str/int) or a sequence array of stop codes.

        Returns:
            A single BusStop object if a scalar input was provided, a list of BusStop 
            objects if a sequence was provided, or None if no matches were located.
        """
        raw_stops = self._fetch_raw_all_stops()

        if isinstance(bus_stop_codes, (str, int)):
            target_code = str(bus_stop_codes)
            for item in raw_stops:
                if str(item.get("BusStopCode")) == target_code:
                    return BusStop(**item)
            return None

        search_set = {str(code) for code in bus_stop_codes}
        return [
            BusStop(**item)
            for item in raw_stops
            if str(item.get("BusStopCode")) in search_set
        ]

    async def async_get_stops(self, bus_stop_codes: str | int | list[str | int]) -> list[BusStop] | BusStop | None:
        """Asynchronously retrieves targeted bus stop configurations from the complete database."""
        raw_stops = await self._async_fetch_raw_all_stops()

        if isinstance(bus_stop_codes, (str, int)):
            target_code = str(bus_stop_codes)
            for item in raw_stops:
                if str(item.get("BusStopCode")) == target_code:
                    return BusStop(**item)
            return None

        search_set = {str(code) for code in bus_stop_codes}
        return [
            BusStop(**item)
            for item in raw_stops
            if str(item.get("BusStopCode")) in search_set
        ]

    def get_all_stops(self) -> list[BusStop]:
        """Fetches all bus stop configurations registered on the LTA network."""
        return [BusStop(**item) for item in self._fetch_raw_all_stops()]

    async def async_get_all_stops(self) -> list[BusStop]:
        """Asynchronously fetches all bus stop configurations registered on the LTA network."""
        return [BusStop(**item) for item in await self._async_fetch_raw_all_stops()]

    def _fetch_raw_all_stops(self) -> list[dict[str, Any]]:
        """Internal helper to download raw payload dictionaries before class instantiation."""
        stops: list[dict[str, Any]] = []
        skip_offset = 0

        while True:
            response = self.send("BusStops", params={"$skip": skip_offset})
            records = response.get("value")

            if not isinstance(records, list) or not records:
                if skip_offset == 0:
                    raise ValueError("LTA DataMall API returned an empty or invalid BusStops payload.")
                break
            stops.extend(records)

            if len(records) < 500:
                break
            skip_offset += 500
        return stops

    async def _async_fetch_raw_all_stops(self) -> list[dict[str, Any]]:
        """Internal helper to asynchronously download raw payload dictionaries."""
        stops: list[dict[str, Any]] = []
        skip_offset = 0

        while True:
            response = await self.async_send("BusStops", params={"$skip": skip_offset}, json=None)
            records = response.get("value")

            if not isinstance(records, list) or not records:
                if skip_offset == 0:
                    raise ValueError("LTA DataMall API returned an empty or invalid BusStops payload.")
                break
            stops.extend(records)

            if len(records) < 500:
                break
            skip_offset += 500
        return stops
