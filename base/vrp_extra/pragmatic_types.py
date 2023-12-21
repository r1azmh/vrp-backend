# Contains semi-automatically generated non-complete model of pragmatic format.
# Please refer to documentation to define a full model

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from pydantic.dataclasses import dataclass


# Routing matrix

# @dataclass
class RoutingMatrix(BaseModel):
    profile: str
    durations: List[int]
    distances: List[int]


# Problem

# @dataclass
class Problem(BaseModel):
    plan: Plan
    fleet: Fleet
    objectives: Optional[List[List[Objective]]] = None


# @dataclass
class Plan(BaseModel):
    jobs: List[Job]
    relations: Optional[List[Relation]] = None


# @dataclass
class Job(BaseModel):
    id: str
    pickups: Optional[List[JobTask]] = None
    deliveries: Optional[List[JobTask]] = None


# @dataclass
class JobTask(BaseModel):
    places: List[JobPlace]
    demand: List[int]


# @dataclass
class JobPlace(BaseModel):
    location: Location
    duration: float
    times: Optional[List[List[datetime]]] = None
    tag: Optional[str] = None


# @dataclass
class VehicleReload(BaseModel):
    location: Location
    duration: float


# @dataclass
class Location(BaseModel):
    lat: float
    lng: float


# @dataclass
class Relation(BaseModel):
    type: str
    jobs: List[str]
    vehicleId: str


# @dataclass
class Fleet(BaseModel):
    vehicles: List[VehicleType]
    profiles: List[RoutingProfile]


# @dataclass
class VehicleType(BaseModel):
    typeId: str
    vehicleIds: List[str]
    profile: VehicleProfile
    costs: VehicleCosts
    shifts: List[VehicleShift]
    capacity: List[int]


# @dataclass
class VehicleProfile(BaseModel):
    matrix: str


# @dataclass
class VehicleCosts(BaseModel):
    fixed: float
    distance: float
    time: float


# @dataclass
class VehicleShift(BaseModel):
    start: VehicleShiftStart
    end: VehicleShiftEnd
    breaks: Optional[List[VehicleBreak]] = None
    reloads: Optional[List[VehicleReload]] = None


# @dataclass
class VehicleShiftStart(BaseModel):
    earliest: datetime
    location: Location
    latest: Optional[datetime] = None


# @dataclass
class VehicleShiftEnd(BaseModel):
    latest: datetime
    location: Location
    earliest: Optional[datetime] = None


# @dataclass
class VehicleBreak(BaseModel):
    time: List[datetime]
    places: List[JobPlace]


# @dataclass
class RoutingProfile(BaseModel):
    name: str


# @dataclass
class Objective(BaseModel):
    type: str
    options: Optional[ObjectiveOptions] = None


# @dataclass
class ObjectiveOptions(BaseModel):
    threshold: float


Problem.model_rebuild()

Plan.model_rebuild()
Job.model_rebuild()
JobTask.model_rebuild()
JobPlace.model_rebuild()

Fleet.model_rebuild()
VehicleReload.model_rebuild()
VehicleType.model_rebuild()
VehicleShift.model_rebuild()
VehicleShiftStart.model_rebuild()
VehicleShiftEnd.model_rebuild()
VehicleBreak.model_rebuild()

Objective.model_rebuild()


# Solution

# @dataclass
class Solution(BaseModel):
    statistic: Statistic
    tours: List[Tour]


# @dataclass
class Statistic(BaseModel):
    cost: float
    distance: int
    duration: int
    times: Times


# @dataclass
class Times(BaseModel):
    driving: int
    serving: int
    waiting: int
    commuting: int
    parking: int


# @dataclass
class Tour(BaseModel):
    vehicleId: str
    typeId: str
    shiftIndex: int
    stops: List[Stop]
    statistic: Statistic


# @dataclass
class Stop(BaseModel):
    location: Location
    time: Schedule
    distance: int
    load: List[int]
    activities: List[Activity]


# @dataclass
class Schedule(BaseModel):
    arrival: datetime
    departure: datetime


# @dataclass
class Activity(BaseModel):
    jobId: str
    type: str
    location: Optional[Location] = None
    time: Optional[Time] = None
    jobTag: Optional[str] = None


# @dataclass
class Time(BaseModel):
    start: datetime
    end: datetime


Solution.model_rebuild()
Statistic.model_rebuild()
Tour.model_rebuild()
Stop.model_rebuild()
Activity.model_rebuild()
