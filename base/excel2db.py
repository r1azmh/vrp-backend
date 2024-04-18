import logging
import os
from enum import Enum

import pandas as pd
from djantic import ModelSchema

from base import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobSchema(ModelSchema):
    class Config:
        model = models.Job


class WorkSchema(ModelSchema):
    class Config:
        model = models.Work


class VehicleSchema(ModelSchema):
    class Config:
        model = models.Vehicle


class FileType(str, Enum):
    csv = '.csv'
    xlsx = '.xlsx'
    json = '.json'


def read_and_write_excel(file_path, schema=JobSchema):
    _, path = os.path.splitext(file_path)
    if path == FileType.csv.value:
        data = pd.read_csv(file_path)
    elif path == FileType.xlsx.value:
        data = pd.read_excel(file_path)
    else:
        raise Exception("file not supported!")

    df_raised_error = schema.parse_df(
        dataframe=data,
        errors="raise",
    )
