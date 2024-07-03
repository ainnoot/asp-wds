from dataclasses import dataclass
from typing import Optional
import shapely

@dataclass(frozen=True)
class Address:
    street_name: str
    civic_number: Optional[int]
    city: str
    country: str

    @property
    def full_name(self):
        parts = [self.street_name, self.city, self.country]
        if self.civic_number is not None:
            parts.insert(1, self.civic_number)
        return ', '.join(str(x) for x in parts)

@dataclass(frozen=True)
class Location:
    lat: float
    lng: float

    def as_tuple(self):
        return self.lat, self.lng

@dataclass(frozen=True)
class GeocodeResponse:
    formatted_address: str
    location: Location
    place_id: str

@dataclass(frozen=True)
class ElevationResponse:
    elevation: float
    location: Location
    resolution: float
