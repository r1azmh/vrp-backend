# Generated by Django 4.2 on 2023-12-06 15:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_alter_job_job_type_alter_job_name_multijob_job_multi'),
    ]

    operations = [
        migrations.AddField(
            model_name='multijob',
            name='work',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.work'),
        ),
    ]
