# Generated by Django 4.2 on 2023-12-24 17:38

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0006_remove_vehicle_type_remove_vehicleprofile_type_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="vehicle",
            old_name="lan",
            new_name="lng",
        ),
    ]
