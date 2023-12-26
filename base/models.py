from django.contrib.auth.models import AbstractUser
from django.db import models

from vrp.mixins.models import AuthorWithTimeStampMixin


# Create your models here.

# class VehicleType(AuthorWithTimeStampMixin):
#     name = models.CharField(max_length=100, null=False, blank=False)
#
#     def __str__(self):
#         return str(self.name)


class VehicleProfile(AuthorWithTimeStampMixin):
    name = models.CharField(max_length=50, null=False, blank=False)
    fixed_cost = models.FloatField(null=False, blank=False)
    distance = models.FloatField(null=False, blank=False)
    time = models.FloatField(null=False, blank=False)

    # type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return str(self.name)


class MultiJob(AuthorWithTimeStampMixin):
    name = models.CharField(max_length=255, null=False, blank=False)
    work = models.ForeignKey("Work", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.name)


class Work(AuthorWithTimeStampMixin):
    name = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return str(self.name)


class Job(AuthorWithTimeStampMixin):
    PICKUP = 'pp'
    DELIVERY = 'dd'
    MULTI = 'mm'
    JOB_TYPES = [
        (PICKUP, 'pickup'),
        (DELIVERY, 'delivery')
    ]

    name = models.CharField(max_length=255, null=True, blank=True)
    lat = models.FloatField(null=False, blank=False)
    lng = models.FloatField(null=False, blank=False)
    job_type = models.CharField(
        max_length=2,
        choices=JOB_TYPES,
        default=PICKUP
    )
    demand = models.IntegerField(null=False, blank=False)
    duration = models.IntegerField(null=False, blank=False)
    start_at = models.CharField(max_length=255, null=True, blank=True)
    end_at = models.CharField(max_length=255, null=True, blank=True)
    work = models.ForeignKey(Work, on_delete=models.CASCADE, null=True, blank=True)
    multi = models.ForeignKey(MultiJob, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.name)


class Vehicle(AuthorWithTimeStampMixin):
    name = models.CharField(max_length=255, null=False, blank=False)
    lat = models.FloatField(null=False, blank=False)
    lng = models.FloatField(null=False, blank=False)
    capacity = models.IntegerField(null=False, blank=False)
    start_at = models.CharField(max_length=100, null=False, blank=False)
    end_at = models.CharField(max_length=100, null=False, blank=False)
    profile = models.ForeignKey(VehicleProfile, on_delete=models.CASCADE, null=False, blank=False)
    # type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, null=False, blank=False, default=1)
    work = models.ForeignKey(Work, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return str(self.profile.name)
