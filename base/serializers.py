import json

from django.core.validators import FileExtensionValidator
from rest_framework import serializers

from . import models


class CategorySerializer(serializers.ModelSerializer):
    total_jobs = serializers.SerializerMethodField()

    class Meta:
        model = models.Category
        fields = '__all__'

    def get_total_jobs(self, category: models.Category):
        return category.job.count()


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
    work_id = serializers.PrimaryKeyRelatedField(source='work',
                                                 queryset=models.Work.objects.all())
    category_id = serializers.PrimaryKeyRelatedField(source="category", queryset=models.Category.objects.all(), allow_null=True, required=False)

    class Meta:
        model = models.Job
        fields = "__all__"


class JobPostSerializer(serializers.ModelSerializer):
    work_id = serializers.PrimaryKeyRelatedField(source='work',
                                                 queryset=models.Work.objects.all())
    category_id = serializers.IntegerField(source="category", allow_null=True, required=False)

    class Meta:
        model = models.Job
        fields = "__all__"


class JobSerializerWithFreshnessPenalty(serializers.ModelSerializer):
    work_id = serializers.PrimaryKeyRelatedField(source='work',
                                                 queryset=models.Work.objects.all())
    category = CategorySerializer(read_only=True)
    arrival_time = serializers.DateTimeField(allow_null=True, required=False)
    f_penalty = serializers.SerializerMethodField()

    class Meta:
        model = models.Job
        fields = "__all__"

    def get_f_penalty(self, job):
        return None


class MultiJobSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    jobs = JobSerializer(many=True)
    work_id = serializers.PrimaryKeyRelatedField(queryset=models.Work.objects.all())


class BulkJobCreate(serializers.Serializer):
    work_id = serializers.PrimaryKeyRelatedField(queryset=models.Work.objects.all())
    file = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=['csv'])])


class VehicleSerializer(serializers.ModelSerializer):
    work_id = serializers.PrimaryKeyRelatedField(source='work',
                                                 queryset=models.Work.objects.all())
    profile_id = serializers.PrimaryKeyRelatedField(source='profile',
                                                    queryset=models.VehicleProfile.objects.all())
    work = WorkSerializer(read_only=True)
    profile = VehicleProfileSerializer(read_only=True)

    class Meta:
        model = models.Vehicle
        fields = "__all__"

class VehicleBulkSerializer(serializers.ModelSerializer):
    work_id = serializers.PrimaryKeyRelatedField(source='work',
                                                 queryset=models.Work.objects.all())
    profile_id = serializers.PrimaryKeyRelatedField(source='profile',
                                                    queryset=models.VehicleProfile.objects.all())
    work = WorkSerializer(read_only=True)
    profile = VehicleProfileSerializer(read_only=True)

    class Meta:
        model = models.Vehicle
        fields = "__all__"



class MultiSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MultiJob
        fields = "__all__"


class MultiJobSerializerGet(serializers.ModelSerializer):
    work = WorkSerializer()
    work_id = serializers.PrimaryKeyRelatedField(source='work',
                                                 queryset=models.Work.objects.all())
    multi = MultiSerializer()

    class Meta:
        model = models.Job
        fields = "__all__"


class Test(serializers.Serializer):
    name = serializers.CharField()
    age = serializers.IntegerField()


class SolutionSerializer(serializers.ModelSerializer):
    work = WorkSerializer()

    class Meta:
        model = models.Solution
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['solution'] = json.loads(data['solution'])
        return data


class FreshnessPenaltySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FreshnessPenalty
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['freshness_penalty'] = json.loads(data['freshness_penalty'])
        return data
