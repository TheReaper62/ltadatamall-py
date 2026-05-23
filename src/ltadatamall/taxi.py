from typing import Union

from .base import BaseModel

__all = (
    'TaxiManager',
    'AvailableTaxi',
    'TaxiStand',
)

class AvailableTaxi:
    def __init__(self,**kwargs):
        self.latitude = float(kwargs.get('Latitude',0))
        self.longitude = float(kwargs.get('Longitude',0))

class TaxiStand:
    def __init__(self,**kwargs):
        ownership_map = {
            'LTA' : "Land Transport Authority",
            'CCS' : "Clear Channel Singapore",
            'Private' : "Private",
        }
        self.taxi_code = kwargs.get('TaxiCode', "Not Available")
        self.latitude = float(kwargs.get('Latitude',0))
        self.longitude = float(kwargs.get('Longitude',0))
        self.bfa = kwargs.get('Bfa',"Not Available")
        self.ownership = ownership_map.get(kwargs.get('Ownership',None),"Not Available")
        self.type = kwargs.get('Type',"Not Available")
        self.name = kwargs.get('Name',"Not Available")

class TaxiManager(BaseModel):
    def __init__(self, api_key: str):
        super().__init__(api_key)

    # Available Taxis
    def get_availability(self):
        response = self.send('Taxi-Availability')
        if response.get('value',False):
            return [AvailableTaxi(**i) for i in response['value']]
        raise Exception("API Returned None")

    async def async_get_availability(self):
        response = await self.async_send('Taxi-Availability')
        if response.get('value',False):
            return [AvailableTaxi(**i) for i in response['value']]
        raise Exception("API Returned None")

    # Taxi Stands
    def get_taxi_stands(self,taxi_codes:Union[str,list[str]]=[]):
        response = self.send('TaxiStands')
        taxi_codes = [taxi_codes] if not isinstance(taxi_codes,(tuple,list)) else taxi_codes
        if response.get('value',False):
            return [TaxiStand(**i) for i in response['value'] if i['TaxiCode'] in taxi_codes and taxi_codes!=[]]
        raise Exception("API Returned None")

    async def async_get_taxi_stands(self, taxi_codes: Union[str, list[str]] = []):
        response = await self.async_send('TaxiStands')
        taxi_codes = [taxi_codes] if not isinstance(
            taxi_codes, (tuple, list)) else taxi_codes
        if response.get('value', False):
            return [TaxiStand(**i) for i in response['value'] if i['TaxiCode'] in taxi_codes and taxi_codes != []]
        raise Exception("API Returned None")
