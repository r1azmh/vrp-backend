# Contains semi-automatically generated non-complete model of config format.
# Please refer to documentation to define a full model

from __future__ import annotations
from pydantic.dataclasses import dataclass
from pydantic import BaseModel
from typing import Optional


# @dataclass
class Telemetry(BaseModel):
    progress: Progress


# @dataclass
class Progress(BaseModel):
    enabled: bool
    logBest: int
    logPopulation: int
    dumpPopulation: bool


Telemetry.model_rebuild()


# @dataclass
class Config(BaseModel):
    termination: Termination
    telemetry: Optional[Telemetry] = Telemetry(
        progress=Progress(
            enabled=True,
            logBest=100,
            logPopulation=1000,
            dumpPopulation=False
        )
    )
    environment: Optional[Environment] = None


# @dataclass
class Termination(BaseModel):
    maxTime: Optional[int] = None
    maxGenerations: Optional[int] = None


# @dataclass
class Logging(BaseModel):
    enabled: bool


Logging.model_rebuild()


# @dataclass
class Environment(BaseModel):
    logging: Logging = Logging(enabled=True)
    isExperimental: Optional[bool] = None


Config.model_rebuild()
Telemetry.model_rebuild()
Termination.model_rebuild()
Environment.model_rebuild()
