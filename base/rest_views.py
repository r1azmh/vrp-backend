from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from . import serializers, filters, models


@api_view(['POST'])
def work_post(request):
    if request.method == 'POST':
        serializer = serializers.WorkSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response({"message": "Hello, world!"})


@api_view(["POST"])
def job_post(request):
    if request.method == "POST":
        serializer = serializers.JobSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response({"message": "Hello, world!"})


@api_view(["GET"])
def job_get(request):
    if request.method == "GET":
        result = filters.WorkFilter(request.GET, queryset=models.Job.objects.all())
        serializer = serializers.MultiJobSerializerGet(result.qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@transaction.atomic
def multi_job_post(request):
    if request.method == "POST":
        serializer = serializers.MultiJobSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            multi_job = models.MultiJob(name=serializer.data.get('name'),
                                        work_id=serializer.data.get('work_id'))
            multi_job.save()
            for job in serializer.data.get('jobs', []):
                job_serializer = serializers.JobSerializer(data=job)
                if job_serializer.is_valid():
                    validate_data = job_serializer.data
                    validate_data['multi_id'] = multi_job.id
                    validate_data['multi'] = multi_job.id
                    job_serializer = serializers.JobSerializer(data=validate_data)
                    if job_serializer.is_valid(raise_exception=True):
                        job_serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response({"message": "Hello, world!"})


@api_view(["DELETE"])
def job_delete(request, pk):
    result = get_object_or_404(models.Job, pk=pk)
    result.delete()
    return Response({"details": "ok"}, status=status.HTTP_202_ACCEPTED)



@api_view(["GET"])
def get_work(request):
    if request.method == "GET":
        result = filters.WorkFilter(request.GET, queryset=models.Work.objects \
                                    .prefetch_related('job_set') \
                                    .prefetch_related('vehicle_set').all())
        serializer = serializers.WorkSerializer(result.qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_work(request, pk):
    result = get_object_or_404(models.Work, pk=pk)
    result.delete()
    return Response({"details": "ok"}, status=status.HTTP_202_ACCEPTED)


@api_view(["GET"])
def vehicle_get(request):
    if request.method == "GET":
        result = filters.WorkFilter(request.GET, queryset=models.Vehicle.objects.all())
        serializer = serializers.VehicleSerializer(result.qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(["GET"])
# def vehicle_profile_get(request):
#     if request.method == "GET":
#         result = filters.WorkFilter(request.GET, queryset=models.VehicleProfile.objects.all())
#         serializer = serializers.VehicleProfileSerializer(result.qs, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def vehicle_bulk_post(request):
    if request.method == "POST":
        serializer = serializers.VehicleSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def vehicle_delete(request, pk):
    result = get_object_or_404(models.Vehicle, pk=pk)
    result.delete()
    return Response({"details": "ok"}, status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
def vehicle_profile_post(request):
    if request.method == 'POST':
        serializer = serializers.VehicleProfileSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response({"message": "Hello, world!"})


@api_view(["GET"])
def vehicle_profile_get(request):
    if request.method == "GET":
        result = filters.WorkFilter(request.GET, queryset=models.VehicleProfile.objects \
                                    .prefetch_related('vehicle_set').all())
        serializer = serializers.VehicleProfileSerializer(result.qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_vehicle_profile(request, pk):
    result = get_object_or_404(models.VehicleProfile, pk=pk)
    result.delete()
    return Response({"details": "ok"}, status=status.HTTP_202_ACCEPTED)
