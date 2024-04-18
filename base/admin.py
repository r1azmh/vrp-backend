from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.Work)
admin.site.register(models.Job)
admin.site.register(models.Vehicle)
admin.site.register(models.Category)
admin.site.register(models.VehicleProfile)
