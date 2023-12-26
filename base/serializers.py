from rest_framework import serializers

from . import models


class VehicleProfileSerializer(serializers.ModelSerializer):
    total_vehicles = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.VehicleProfile
        fields = "__all__"

    def get_total_vehicles(self, obj):
        return obj.vehicle_set.count()


class WorkSerializer(serializers.ModelSerializer):
    total_jobs = serializers.SerializerMethodField()
    total_vehicles = serializers.SerializerMethodField()

    class Meta:
        model = models.Work
        fields = "__all__"

    def get_total_jobs(self, obj):
        return obj.job_set.count()

    def get_total_vehicles(self, obj):
        return obj.vehicle_set.count()


class JobSerializer(serializers.ModelSerializer):
    work_id = serializers.PrimaryKeyRelatedField(source='work', queryset=models.Work.objects.all())

    class Meta:
        model = models.Job
        fields = "__all__"


class MultiJobSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    jobs = JobSerializer(many=True)
    work_id = serializers.PrimaryKeyRelatedField(queryset=models.Work.objects.all())


class VehicleSerializer(serializers.ModelSerializer):
    work_id = serializers.PrimaryKeyRelatedField(source='work', queryset=models.Work.objects.all())
    profile_id = serializers.PrimaryKeyRelatedField(source='profile', queryset=models.VehicleProfile.objects.all())

    class Meta:
        model = models.Vehicle
        fields = ['id', 'name', 'lat', 'lng', 'capacity', 'start_at', 'end_at', 'profile_id', 'work_id']


# class VehicleProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.VehicleProfile
#         fields = "__all__"


class MultiSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MultiJob
        fields = "__all__"


class MultiJobSerializerGet(serializers.ModelSerializer):
    work_id = serializers.PrimaryKeyRelatedField(source='work', queryset=models.Work.objects.all())
    multi = MultiSerializer()
    class Meta:
        model = models.Job
        fields = "__all__"

