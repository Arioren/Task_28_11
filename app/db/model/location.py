from dataclasses import dataclass


@dataclass
class Location:
    latitude: float
    longitude: float
    altitude_meters: int
    accuracy_meters: int