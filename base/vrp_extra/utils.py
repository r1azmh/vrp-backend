from typing import List

from base import models
from base.vrp_extra import pragmatic_types as prg


def get_vehicle(_vehicle: models.Vehicle):
    return {"v_type": prg.VehicleType(
        typeId=_vehicle.type.name,
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
                    location=prg.Location(lat=_vehicle.lat, lng=_vehicle.lan),
                ),
                end=prg.VehicleShiftEnd(
                    latest=_vehicle.end_at,
                    location=prg.Location(lat=_vehicle.lat, lng=_vehicle.lan),
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
    time = []
    if _job.start_at and _job.end_at:
        time.append([_job.start_at, _job.end_at])
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
    # jobs = [get_job(_job) for _job in _jobs]

    return prg.Job(
        id=job.name,
        deliveries=[get_job_task(_job) for _job in jobs if _job.job_type == 'dd'],
        pickups=[get_job_task(_job) for _job in jobs if _job.job_type == 'pp'],
    )
