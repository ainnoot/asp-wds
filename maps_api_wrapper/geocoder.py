from typing import Sequence, Optional
import googlemaps
from maps_api_wrapper.model import GeocodeResponse, ElevationResponse, Location, Address
import os
class MapsAPI:
    def __init__(self):
        GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
        if GOOGLE_MAPS_API_KEY is None:
            raise RuntimeError("Unavailable Google Maps API key. Remember to export GOOGLE_MAPS_API_KEY!")

        self.client = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

    def inverse_geocode(self, address: Address) -> Optional[GeocodeResponse]:

        response = self.client.geocode(address.full_name)
        if len(response) == 0:
            return None

        return GeocodeResponse(
            response[0]['formatted_address'],
            Location(
                response[0]['geometry']['location']['lat'],
                response[0]['geometry']['location']['lng']
            ),
            response[0]['place_id']
        )

    def elevation(self, locations: Sequence[Location]) -> Sequence[ElevationResponse]:
        response = self.client.elevation([loc.as_tuple() for loc in locations])
        results = []
        for ans in response:
            loc = Location(ans['location']['lat'], ans['location']['lng'])
            results.append(ElevationResponse(ans['elevation'], loc, ans['resolution']))
        return results
