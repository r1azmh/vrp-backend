# Contains semi-automatically generated non-complete model of pragmatic format.
# Please refer to documentation to define a full model

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# Routing matrix


class RoutingMatrix(BaseModel):
    profile: str
    durations: List[int]
    distances: List[int]


# Problem


class Problem(BaseModel):
    plan: Plan
    fleet: Fleet
    objectives: Optional[List[List[Objective]]] = None


class Plan(BaseModel):
    jobs: List[Job]
    relations: Optional[List[Relation]] = None


class Job(BaseModel):
    id: str
    pickups: Optional[List[JobTask]] = None
    deliveries: Optional[List[JobTask]] = None


class JobTask(BaseModel):
    places: List[JobPlace]
    demand: List[int]


class JobPlace(BaseModel):
    location: Location
    duration: float
    times: Optional[List[List[datetime]]] = None
    tag: Optional[str] = None


class VehicleReload(BaseModel):
    location: Location
    duration: float


class Location(BaseModel):
    lat: float
    lng: float


class Relation(BaseModel):
    type: str
    jobs: List[str]
    vehicleId: str


class Fleet(BaseModel):
    vehicles: List[VehicleType]
    profiles: List[RoutingProfile]


class VehicleType(BaseModel):
    typeId: str
    vehicleIds: List[str]
    profile: VehicleProfile
    costs: VehicleCosts
    shifts: List[VehicleShift]
    capacity: List[int]


class VehicleProfile(BaseModel):
    matrix: str
    speed: Optional[int] = None


class VehicleCosts(BaseModel):
    fixed: float
    distance: float
    time: float


class VehicleShift(BaseModel):
    start: VehicleShiftStart
    end: VehicleShiftEnd
    breaks: Optional[List[VehicleBreak]] = None
    reloads: Optional[List[VehicleReload]] = None


class VehicleShiftStart(BaseModel):
    earliest: datetime
    location: Location
    latest: Optional[datetime] = None


class VehicleShiftEnd(BaseModel):
    latest: datetime
    location: Location
    earliest: Optional[datetime] = None


class VehicleBreak(BaseModel):
    time: List[datetime]
    places: List[JobPlace]


class RoutingProfile(BaseModel):
    name: str
    speed: Optional[float] = None


class Objective(BaseModel):
    type: str
    options: Optional[ObjectiveOptions] = None


class ObjectiveOptions(BaseModel):
    threshold: float


# Solution


class Solution(BaseModel):
    statistic: Statistic
    tours: List[Tour]


class Statistic(BaseModel):
    cost: float
    distance: int
    duration: int
    times: Times


class Times(BaseModel):
    driving: int
    serving: int
    waiting: int
    commuting: int
    parking: int


class Tour(BaseModel):
    vehicleId: str
    typeId: str
    shiftIndex: int
    stops: List[Stop]
    statistic: Statistic


class Stop(BaseModel):
    location: Location
    time: Schedule
    distance: int
    load: List[int]
    activities: List[Activity]


class Schedule(BaseModel):
    arrival: datetime
    departure: datetime


class Activity(BaseModel):
    jobId: str
    type: str
    location: Optional[Location] = None
    time: Optional[Time] = None
    jobTag: Optional[str] = None


class Time(BaseModel):
    start: datetime
    end: datetime
