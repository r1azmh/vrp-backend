from enum import Enum
from itertools import chain
from typing import Tuple, List

import openrouteservice as ors


def flatten(matrix):
    return list(chain.from_iterable(matrix))


class EnumRouteVehicleProfile(str, Enum):
    DRIVING_CAR = "driving-car"
    DRIVING_HGV = "driving-hgv"
    FOOT_WALKING = "foot-walking"
    FOOT_HIKING = "foot-hiking"
    CYCLING_REGULAR = "cycling-regular"
    CYCLING_ROAD = "cycling-road"
    CYCLING_SAFE = "cycling-safe"
    CYCLING_MOUNTAIN = "cycling-mountain"
    CYCLING_TOUR = "cycling-tour"
    CYCLING_ELECTRIC = "cycling-electric"


client = ors.Client(key='5b3ce3597851110001cf6248dd61e0bf7f4a4cdbaf06323a168b0b59')


def get_routing_matrix(locations: List[List[float]], profile: EnumRouteVehicleProfile) -> Tuple[List, List]:
    distances = []
    durations = []
    mat = client.distance_matrix(locations=locations, metrics=["distance",
                                                               "duration"], profile=profile)
    if "durations" in mat and "distances" in mat:
        distances = flatten(mat["distances"])
        durations = flatten(mat["durations"])
    return durations, distances
