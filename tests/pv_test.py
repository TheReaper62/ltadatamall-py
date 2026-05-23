from typing import Any
from unittest.mock import MagicMock, AsyncMock
import pytest

from ltadatamall.passenger_volume import PassengerVolume


@pytest.fixture
def pv_manager() -> PassengerVolume:
    """Fixture to provide a clean PassengerVolume instance for every isolated test run."""
    return PassengerVolume(api_key="mock_secret_lta_account_key")


@pytest.fixture
def mock_success_payload() -> dict[str, list[dict[str, str]]]:
    """Provides a sample successful LTA DataMall S3 download response dictionary."""
    return {
        "value": [
            {
                "Link": "https://datamall2.mytransport.sg/ltaodataservice/download/pv_bus_202601.zip"
            }
        ]
    }


@pytest.fixture
def mock_malformed_payload() -> dict[str, list[Any]]:
    """Provides a malformed payload missing the target link structural data."""
    return {"value": [{"NotALink": "broken_data"}]}


# 1. SYNCHRONOUS ENDPOINT TESTS
def test_pv_bus_stop_with_date(
    pv_manager: PassengerVolume, mock_success_payload: dict[str, Any]
) -> None:
    pv_manager.send = MagicMock(return_value=mock_success_payload)

    link = pv_manager.pv_bus_stop(date="202603")

    assert (
        link
        == "https://datamall2.mytransport.sg/ltaodataservice/download/pv_bus_202601.zip"
    )
    pv_manager.send.assert_called_once_with("PV/Bus", params={"Date": "202603"})


def test_pv_od_bus_stop_without_date(
    pv_manager: PassengerVolume, mock_success_payload: dict[str, Any]
) -> None:
    pv_manager.send = MagicMock(return_value=mock_success_payload)

    link = pv_manager.pv_od_bus_stop(date=None)

    assert (
        link
        == "https://datamall2.mytransport.sg/ltaodataservice/download/pv_bus_202601.zip"
    )
    pv_manager.send.assert_called_once_with("PV/ODBus", params=None)


def test_pv_od_train_destination_success(
    pv_manager: PassengerVolume, mock_success_payload: dict[str, Any]
) -> None:
    pv_manager.send = MagicMock(return_value=mock_success_payload)

    link = pv_manager.pv_od_train_destination(date="202604")

    assert (
        link
        == "https://datamall2.mytransport.sg/ltaodataservice/download/pv_bus_202601.zip"
    )
    pv_manager.send.assert_called_once_with("PV/ODTrain", params={"Date": "202604"})


def test_pv_train_station_success(
    pv_manager: PassengerVolume, mock_success_payload: dict[str, Any]
) -> None:
    pv_manager.send = MagicMock(return_value=mock_success_payload)

    link = pv_manager.pv_train_station(date="202605")

    assert (
        link
        == "https://datamall2.mytransport.sg/ltaodataservice/download/pv_bus_202601.zip"
    )
    pv_manager.send.assert_called_once_with("PV/Train", params={"Date": "202605"})


# 2. ASYNCHRONOUS ENDPOINT TESTS (Labeled with Async Markers)
@pytest.mark.asyncio
async def test_async_pv_bus_stop_success(
    pv_manager: PassengerVolume, mock_success_payload: dict[str, Any]
) -> None:
    pv_manager.async_send = AsyncMock(return_value=mock_success_payload)

    link = await pv_manager.async_pv_bus_stop(date="202603")

    assert (
        link
        == "https://datamall2.mytransport.sg/ltaodataservice/download/pv_bus_202601.zip"
    )
    pv_manager.async_send.assert_called_once_with(
        "PV/Bus", params={"Date": "202603"}, json=None
    )


@pytest.mark.asyncio
async def test_async_pv_od_bus_stop_success(
    pv_manager: PassengerVolume, mock_success_payload: dict[str, Any]
) -> None:
    pv_manager.async_send = AsyncMock(return_value=mock_success_payload)

    link = await pv_manager.async_pv_od_bus_stop(date=None)

    assert (
        link
        == "https://datamall2.mytransport.sg/ltaodataservice/download/pv_bus_202601.zip"
    )
    pv_manager.async_send.assert_called_once_with("PV/ODBus", params=None, json=None)


@pytest.mark.asyncio
async def test_async_pv_od_train_destination_success(
    pv_manager: PassengerVolume, mock_success_payload: dict[str, Any]
) -> None:
    pv_manager.async_send = AsyncMock(return_value=mock_success_payload)

    link = await pv_manager.async_pv_od_train_destination(date="202604")

    assert (
        link
        == "https://datamall2.mytransport.sg/ltaodataservice/download/pv_bus_202601.zip"
    )
    pv_manager.async_send.assert_called_once_with(
        "PV/ODTrain", params={"Date": "202604"}, json=None
    )


@pytest.mark.asyncio
async def test_async_pv_train_station_success(
    pv_manager: PassengerVolume, mock_success_payload: dict[str, Any]
) -> None:
    pv_manager.async_send = AsyncMock(return_value=mock_success_payload)

    link = await pv_manager.async_pv_train_station(date="202605")

    assert (
        link
        == "https://datamall2.mytransport.sg/ltaodataservice/download/pv_bus_202601.zip"
    )
    pv_manager.async_send.assert_called_once_with(
        "PV/Train", params={"Date": "202605"}, json=None
    )


# 3. DEFENSIVE DATA ERROR HANDLING TESTS
def test_extract_download_link_raises_value_error_on_empty_list(
    pv_manager: PassengerVolume,
) -> None:
    # Testing condition where 'value' field returns an empty collection response []
    empty_payload = {"value": []}
    pv_manager.send = MagicMock(return_value=empty_payload)

    with pytest.raises(
        ValueError,
        match="LTA DataMall API did not yield a valid download link structural layout for endpoint: 'PV/Bus'",
    ):
        pv_manager.pv_bus_stop()


def test_extract_download_link_raises_value_error_on_malformed_keys(
    pv_manager: PassengerVolume, mock_malformed_payload: dict[str, Any]
) -> None:
    # Testing condition where data entries are mapped but the target 'Link' identifier key is completely absent
    pv_manager.send = MagicMock(return_value=mock_malformed_payload)

    with pytest.raises(
        ValueError,
        match="LTA DataMall API did not yield a valid download link structural layout for endpoint: 'PV/Train'",
    ):
        pv_manager.pv_train_station()
