from django.forms import ModelForm

from . import models


class JobForm(ModelForm):
    class Meta:
        model = models.Job
        fields = "__all__"


class VehicleTypeForm(ModelForm):
    class Meta:
        model = models.VehicleType
        fields = "__all__"


class VehicleProfileForm(ModelForm):
    class Meta:
        model = models.VehicleProfile
        fields = "__all__"


class WorkForm(ModelForm):
    class Meta:
        model = models.Work
        fields = "__all__"


class VehicleForm(ModelForm):
    class Meta:
        model = models.Vehicle
        fields = "__all__"

class MultiJobForm(ModelForm):
    class Meta:
        model = models.MultiJob
        fields = "__all__"
