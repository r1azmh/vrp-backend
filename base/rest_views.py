import json

import vrp_cli
from django.db import transaction
from django.shortcuts import get_object_or_404
from pydantic.json import pydantic_encoder
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from base import serializers, filters, models
from base.vrp_extra import new_pragmatic_types as prg, config_types as cfg
from base.vrp_extra.utils import get_job, get_multi_job, get_vehicles, get_routing_matrix, flatten, get_location, \
    get_vehicle_profile_locations, get_job_locations, EnumRouteVehicleProfile

config = cfg.Config(
    termination=cfg.Termination(
        maxTime=5,
        maxGenerations=1000
    )
)


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


@api_view(["GET"])
def solve(request, pk):
    # data = dict()
    work = models.Work.objects.get(pk=pk)

    _jobs = models.Job.objects.filter(work_id=pk, multi=None)
    _multi_jobs = models.MultiJob.objects.filter(work_id=pk, job__isnull=False).distinct()
    jobs = [get_job(_job) for _job in _jobs]
    multi_jobs = [get_multi_job(_job) for _job in _multi_jobs]

    _vehicles = models.Vehicle.objects.select_related('profile').filter(work_id=pk)

    vehicles, profiles = get_vehicles(_vehicles)
    fleet = prg.Fleet(vehicles=vehicles,
                      profiles=[prg.RoutingProfile(name=profile, speed=16.67) for profile in profiles])
    print('\n\n\n\n fleet \n\n\n', fleet)

    plan = prg.Plan(jobs=jobs + multi_jobs)
    problem = prg.Problem(plan=plan, fleet=fleet)

    # new work

    matrices = []
    custom_matrix = True

    if custom_matrix:
        v_locations = get_vehicle_profile_locations(fleet)
        j_locations = get_job_locations(plan)
        durations, distances = get_routing_matrix(j_locations + v_locations, EnumRouteVehicleProfile.DRIVING_CAR)
        #vj_locations = []
        #durations, distances = get_routing_matrix(vj_locations, EnumRouteVehicleProfile.DRIVING_HGV)
        durations, distances = list(map(lambda x: int(x), durations)), list(map(lambda x: int(x), distances))

        print('\n\n\n\n locations \n\n\n', j_locations + v_locations)
        print('\n\n\n\n durations \n\n\n', durations)
        print('\n\n\n\n  distances \n\n\n', distances)
        matrix = prg.RoutingMatrix(
            profile='normal_car',
            durations=durations,
            # durations=[0, 609, 981, 906, 813, 0, 371, 590, 1055, 514, 0, 439, 948, 511, 463, 0],
            distances=distances
            # distances=[0, 3840, 5994, 5333, 4696, 0, 2154, 3226, 5763, 2674, 0, 2145, 5112, 2470, 2152, 0]
        )
        matrices.append(matrix.model_dump_json())
    solution = prg.Solution(**json.loads(vrp_cli.solve_pragmatic(
        problem=problem.model_dump_json(),
        matrices=matrices,
        config=config.model_dump_json(),
    )))

    # return JsonResponse(
    #     {"data": [job.model_dump() for job in jobs], "problem": problem.model_dump(), "fleet": fleet.model_dump(),
    #      "solution": solution.model_dump()})
    job_serializer = serializers.JobSerializer(_jobs, many=True)
    work_serializer = serializers.WorkSerializer(work)
    vehicle_serializer = serializers.VehicleSerializer(_vehicles, many=True)
    context = {
        "solution": solution.model_dump(),
        "work": work_serializer.data,
        "jobs": job_serializer.data,
        "vehicles": vehicle_serializer.data,

    }
    return Response(context, status=status.HTTP_202_ACCEPTED)
