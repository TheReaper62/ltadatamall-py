from os import getenv
from typing import Any
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from ltadatamall.bus_manager import BusManager
from ltadatamall.bus_stop import BusStop
from ltadatamall.bus_service import BusService
from ltadatamall.bus_route import BusRoute
from ltadatamall.bus_arrival import BusArrivalService


@pytest.fixture
def bus_manager() -> BusManager:
    """Fixture to provide a clean BusManager instance for every isolated test run."""
    return BusManager(api_key=getenv("LTA_DATAMALL_API_KEY"))


# 1. BUS ARRIVAL TESTS (get_bus_arrival / async_get_bus_arrival)
def test_get_bus_arrival_success(bus_manager: BusManager) -> None:
    mock_payload = {
        "Services": [
            {
                "ServiceNo": "190",
                "Operator": "SMRT",
                "NextBus": {"EstimatedArrival": "2026-01-01T12:00:00+08:00"},
            }
        ]
    }
    bus_manager.send = MagicMock(return_value=mock_payload)

    results = bus_manager.get_bus_arrival(bus_stop_code="65009", service_no="190")

    assert isinstance(results, list)
    assert len(results) == 1
    assert isinstance(results[0], BusArrivalService)
    assert results[0].service_no == 190
    bus_manager.send.assert_called_once_with(
        "v3/BusArrival", params={"BusStopCode": "65009", "ServiceNo": "190"}
    )


@pytest.mark.asyncio
async def test_async_get_bus_arrival_success(bus_manager: BusManager) -> None:
    mock_payload = {
        "Services": [
            {
                "ServiceNo": "960",
                "Operator": "SMRT",
                "NextBus": {"EstimatedArrival": "2026-01-01T12:05:00+08:00"},
            }
        ]
    }
    bus_manager.async_send = AsyncMock(return_value=mock_payload)

    results = await bus_manager.async_get_bus_arrival(bus_stop_code=65009)

    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0].service_no == 960
    bus_manager.async_send.assert_called_once_with(
        "v3/BusArrival", params={"BusStopCode": "65009"}, json=None
    )


def test_get_bus_arrival_raises_value_error(bus_manager: BusManager) -> None:
    bus_manager.send = MagicMock(return_value={"Services": None})

    with pytest.raises(
        ValueError, match="LTA DataMall API did not yield any service items"
    ):
        bus_manager.get_bus_arrival(bus_stop_code="12345")


# 2. BUS SERVICES TESTS (get_services / async_get_services)
@pytest.fixture
def sample_services_payload() -> dict[str, Any]:
    return {
        "value": [
            {
                "ServiceNo": "2",
                "Operator": "SBST",
                "Direction": 1,
                "Category": "FREEWAY",
            },
            {"ServiceNo": "12", "Operator": "GAS", "Direction": 1, "Category": "TRUNK"},
            {
                "ServiceNo": "190",
                "Operator": "SMRT",
                "Direction": 2,
                "Category": "TRUNK",
            },
        ]
    }


def test_get_services_no_filter(
    bus_manager: BusManager, sample_services_payload: dict[str, Any]
) -> None:
    bus_manager.send = MagicMock(return_value=sample_services_payload)

    results = bus_manager.get_services()

    assert len(results) == 3
    assert all(isinstance(s, BusService) for s in results)
    assert results[0].service_no == "2"


def test_get_services_with_filter(
    bus_manager: BusManager, sample_services_payload: dict[str, Any]
) -> None:
    bus_manager.send = MagicMock(return_value=sample_services_payload)

    results = bus_manager.get_services(services=["12", 190])

    assert len(results) == 2
    service_numbers = {s.service_no for s in results}
    assert service_numbers == {"12", "190"}


@pytest.mark.asyncio
async def test_async_get_services_filtered(
    bus_manager: BusManager, sample_services_payload: dict[str, Any]
) -> None:
    bus_manager.async_send = AsyncMock(return_value=sample_services_payload)

    results = await bus_manager.async_get_services(services=["2"])

    assert len(results) == 1
    assert results[0].service_no == "2"
    bus_manager.async_send.assert_called_once_with(
        "BusServices", params=None, json=None
    )


# 3. BUS SERVICES PAGINATION TESTS (get_all_services / async_get_all_services)
def test_get_all_services_pagination(bus_manager: BusManager) -> None:
    page_1 = {"value": [{"ServiceNo": "A"} for _ in range(500)]}
    page_2 = {"value": [{"ServiceNo": "B"} for _ in range(200)]}

    bus_manager.send = MagicMock(side_effect=[page_1, page_2])

    results = bus_manager.get_all_services()

    assert len(results) == 700
    assert bus_manager.send.call_count == 2
    bus_manager.send.assert_any_call("BusServices", params={"$skip": 0})
    bus_manager.send.assert_any_call("BusServices", params={"$skip": 500})


@pytest.mark.asyncio
async def test_async_get_all_services_pagination(bus_manager: BusManager) -> None:
    page_1 = {"value": [{"ServiceNo": "A"} for _ in range(500)]}
    page_2 = {"value": []}

    bus_manager.async_send = AsyncMock(side_effect=[page_1, page_2])

    results = await bus_manager.async_get_all_services()

    assert len(results) == 500
    assert bus_manager.async_send.call_count == 2


# 4. BUS ROUTES TESTS (get_routes / async_get_routes / pagination)
@pytest.fixture
def sample_routes_payload() -> dict[str, Any]:
    return {
        "value": [
            {
                "ServiceNo": "190",
                "BusStopCode": "65009",
                "Direction": 1,
                "StopSequence": 5,
            },
            {
                "ServiceNo": "190",
                "BusStopCode": "11111",
                "Direction": 1,
                "StopSequence": 6,
            },
            {
                "ServiceNo": "960",
                "BusStopCode": "65009",
                "Direction": 2,
                "StopSequence": 12,
            },
        ]
    }


def test_get_routes_with_snake_case_normalization(
    bus_manager: BusManager, sample_routes_payload: dict[str, Any]
) -> None:
    bus_manager.send = MagicMock(return_value=sample_routes_payload)

    results = bus_manager.get_routes(service_no="190", bus_stop_code="65009")

    assert len(results) == 1
    assert isinstance(results[0], BusRoute)
    assert results[0].bus_stop_code == "65009"
    assert results[0].service_no == "190"


@pytest.mark.asyncio
async def test_async_get_routes_no_filters(
    bus_manager: BusManager, sample_routes_payload: dict[str, Any]
) -> None:
    bus_manager.async_send = AsyncMock(return_value=sample_routes_payload)

    results = await bus_manager.async_get_routes()

    assert len(results) == 3
    assert all(isinstance(r, BusRoute) for r in results)


def test_get_all_routes_pagination_error_on_first_call(bus_manager: BusManager) -> None:
    bus_manager.send = MagicMock(return_value={"value": None})

    with pytest.raises(
        ValueError,
        match="LTA DataMall API returned an empty or invalid BusRoutes payload",
    ):
        bus_manager.get_all_routes()


# 5. BUS STOPS TESTS (get_stops / async_get_stops)
@pytest.fixture
def sample_stops_payload() -> list[dict[str, Any]]:
    return [
        {"BusStopCode": "65009", "RoadName": "Central Exp", "Description": "Blk 123"},
        {"BusStopCode": "11111", "RoadName": "Orchard Rd", "Description": "Opp Plaza"},
        {"BusStopCode": "02029", "RoadName": "Victoria St", "Description": "Bugis Stn"},
    ]


def test_get_stops_single_scalar_input(
    bus_manager: BusManager, sample_stops_payload: list[dict[str, Any]]
) -> None:
    bus_manager._fetch_raw_all_stops = MagicMock(return_value=sample_stops_payload)

    result = bus_manager.get_stops(bus_stop_codes=11111)

    assert isinstance(result, BusStop)
    assert result.bus_stop_code == "11111"
    assert result.road_name == "Orchard Rd"


def test_get_stops_sequence_array_input(
    bus_manager: BusManager, sample_stops_payload: list[dict[str, Any]]
) -> None:
    bus_manager._fetch_raw_all_stops = MagicMock(return_value=sample_stops_payload)

    results = bus_manager.get_stops(bus_stop_codes=["65009", "02029", "99999"])

    assert isinstance(results, list)
    assert len(results) == 2
    codes = {s.bus_stop_code for s in results}
    assert codes == {"65009", "02029"}


@pytest.mark.asyncio
async def test_async_get_stops_not_found(
    bus_manager: BusManager, sample_stops_payload: list[dict[str, Any]]
) -> None:
    bus_manager._async_fetch_raw_all_stops = AsyncMock(
        return_value=sample_stops_payload
    )

    result = await bus_manager.async_get_stops(bus_stop_codes="NON_EXISTENT")

    assert result is None
