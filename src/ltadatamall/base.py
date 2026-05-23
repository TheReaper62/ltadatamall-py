'''
Authors: TheReaper62
'''

from typing import Any, Optional

import httpx
from requests import Session, exceptions


class BaseModel:
    """
    Base class for all model classes.
    Contains the send and async_send methods for sending requests to the API.
    """

    BASE_URL = "https://datamall2.mytransport.sg/ltaodataservice"

    def __init__(self, api_key: str):
        self.headers = {"Accept": "application/json", "AccountKey": api_key}

    def send(
        self,
        path,
        *,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Sends a request to the API and returns the response as a JSON object."""
        with Session() as session:
            response = session.get(
                BaseModel.BASE_URL + "/" + path,
                params=params,
                headers=self.headers,
                json=json,
            )
            try:
                response.raise_for_status()
                return response.json()
            except exceptions.HTTPError as error:
                raise exceptions.HTTPError(f"An Error Occured: {error}") from None

    async def async_send(
        self, path: str, *, params: dict[str, Any], json: dict[str, Any]
    ) -> dict[str, Any]:
        """Sends an asynchronous request to the API and returns the response as a JSON object."""
        url = f"{BaseModel.BASE_URL}/{path}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url, params=params, headers=self.headers, json=json
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as error:
                # Captures 4xx and 5xx responses specifically
                raise exceptions.HTTPError(f"An Error Occurred: {error}") from None
            except httpx.RequestError as error:
                # Captures underlying network issues (e.g., connection timeouts)
                raise exceptions.HTTPError(
                    f"A Network Error Occurred: {error}"
                ) from None
