from enum import Enum
from itertools import chain
from typing import Tuple, List

import openrouteservice as ors

from base import models
# from base.vrp_extra import pragmatic_types as prg
from base.vrp_extra import new_pragmatic_types as prg


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


def get_routing_matrix(locations: List[List], profile: EnumRouteVehicleProfile) -> Tuple[List, List]:
    distances = []
    durations = []
    mat = client.distance_matrix(locations=locations, metrics=["distance",
                                                               "duration"], profile=profile)
    print(mat)
    if "durations" in mat and "distances" in mat:
        distances = flatten(mat["distances"])
        durations = flatten(mat["durations"])
    return durations, distances


def get_vehicle(_vehicle: models.Vehicle):
    return {"v_type": prg.VehicleType(
        typeId=_vehicle.name,
        vehicleIds=[_vehicle.name],
        profile=prg.VehicleProfile(matrix=_vehicle.profile.name),
        costs=prg.VehicleCosts(
            fixed=_vehicle.profile.fixed_cost,
            distance=_vehicle.profile.distance,
            time=_vehicle.profile.time),
        shifts=[
            prg.VehicleShift(
                start=prg.VehicleShiftStart(
                    earliest=_vehicle.start_at,
                    location=prg.Location(lat=_vehicle.lat, lng=_vehicle.lng),
                ),
                end=prg.VehicleShiftEnd(
                    latest=_vehicle.end_at,
                    location=prg.Location(lat=_vehicle.lat, lng=_vehicle.lng),
                )
            )
        ],
        capacity=[_vehicle.capacity]
    ), 'profile': _vehicle.profile.name}


def get_vehicles(_vehicles: List[models.Vehicle]):
    v_types = []
    profiles = set()
    for _vehicle in _vehicles:
        data = get_vehicle(_vehicle)
        v_types.append(data['v_type'])
        profiles.add(data['profile'])
    return v_types, profiles


def get_job_task(_job: models.Job):
    time = None
    if _job.start_at and _job.end_at:
        time = [[_job.start_at, _job.end_at]]
    place = [prg.JobPlace(
        location=prg.Location(
            lat=_job.lat,
            lng=_job.lng
        ),
        duration=_job.duration,
        times=time
    )]
    return prg.JobTask(
        places=place,
        demand=[_job.demand]
    )


def get_job(_job: models.Job):
    if _job.job_type == 'pp':
        pickups = get_job_task(_job)
        return prg.Job(
            id=_job.name,
            pickups=[pickups]
        )
    if _job.job_type == 'dd':
        deliveries = get_job_task(_job)
        return prg.Job(
            id=_job.name,
            deliveries=[deliveries]
        )


def get_multi_job(job: models.MultiJob):
    jobs = models.Job.objects.filter(multi=job)
    return prg.Job(
        id=job.name,
        deliveries=[get_job_task(_job) for _job in jobs if _job.job_type == 'dd'],
        pickups=[get_job_task(_job) for _job in jobs if _job.job_type == 'pp'],
    )


def get_location(obj):
    data = []
    if obj.start:
        data.append([obj.start.location.lng, obj.start.location.lat])
    if obj.end:
        if len(data) == 0:
            data.append([obj.end.location.lng, obj.end.location.lat])
        else:
            if data[0] != [obj.end.location.lng, obj.end.location.lat]:
                data.append([obj.end.location.lng, obj.end.location.lat])
    return data


def get_vehicle_profile_locations(fleet: prg.Fleet):
    routing_profile = dict()
    for vehicle in fleet.vehicles:
        route_p = routing_profile.get(vehicle.profile.matrix, None)
        if route_p:
            route_p.append(flatten(flatten([get_location(obj) for obj in vehicle.shifts])))
            routing_profile[vehicle.profile.matrix] = route_p
        else:
            routing_profile[vehicle.profile.matrix] = flatten([get_location(obj) for obj in vehicle.shifts])
    return flatten(routing_profile.values())


def get_job_locations(plan: prg.Plan):
    job_locations = dict()
    for job in plan.jobs:
        if job.pickups:
            for picup in job.pickups:
                for place in picup.places:
                    job_locations[f"{place.location.lng}{place.location.lat}"] = [place.location.lng, place.location.lat]
        if job.deliveries:
            for delivery in job.deliveries:
                for place in delivery.places:
                    job_locations[f"{place.location.lng}{place.location.lat}"] = [place.location.lng, place.location.lat]
    return list(job_locations.values())
