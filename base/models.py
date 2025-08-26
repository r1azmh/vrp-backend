from django.contrib.auth.models import AbstractUser
from django.db import models

from vrp.mixins.models import AuthorWithTimeStampMixin, TimeStampMixin

# Create your models here.

# class VehicleType(AuthorWithTimeStampMixin):
#     name = models.CharField(max_length=100, null=False, blank=False)
#
#     def __str__(self):
#         return str(self.name)



class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, null=False, blank=False)
    penalty = models.FloatField(null=False, blank=False)

    def __str__(self):
        return self.name


class TruckType(models.TextChoices):
    RIGID_3_5_7_5 = "rigid_3_5_7_5", "Rigid (>3.5–7.5 t)"
    RIGID_7_5_17   = "rigid_7_5_17",   "Rigid (>7.5–17 t)"
    RIGID_17_PLUS  = "rigid_17_plus",  "Rigid (>17 t)"
    ARTIC_3_5_33   = "artic_3_5_33",   "Articulated (>3.5–33 t)"
    ARTIC_33_PLUS  = "artic_33_plus",  "Articulated (>33 t)"

class Temperature(models.TextChoices):
    AMBIENT      = "ambient",      "Ambient"
    REFRIGERATED = "refrigerated", "Refrigerated"


class VehicleProfile(AuthorWithTimeStampMixin):
    name = models.CharField(max_length=50, null=False, blank=False)
    fixed_cost = models.FloatField(null=False, blank=False)
    distance = models.FloatField(null=False, blank=False)
    time = models.FloatField(null=False, blank=False)

    # type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, null=False, blank=False)

    # NEW:
    truck_type = models.CharField(
        max_length=32, choices=TruckType.choices, default=TruckType.RIGID_7_5_17
    )
    temperature = models.CharField(
        max_length=16, choices=Temperature.choices, default=Temperature.AMBIENT
    )
    max_capacity = models.PositiveIntegerField(null=False, blank=False, default=1)

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
    
    class Meta:
        ordering = ('-created_at',)


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

    # RELATIONS
    work = models.ForeignKey(Work, on_delete=models.CASCADE, null=True, blank=True)
    multi = models.ForeignKey(MultiJob, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name='job')

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



class Solution(TimeStampMixin):
    solution = models.JSONField(null=False, blank=False)
    work = models.OneToOneField(Work, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        ordering = ('-updated_at',)


class FreshnessPenalty(models.Model):
    freshness_penalty = models.JSONField(null=False, blank=False)
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE, null=False, blank=False)
