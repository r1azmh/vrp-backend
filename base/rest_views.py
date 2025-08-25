import csv
import io
import json
import math
from datetime import datetime

import vrp_cli
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from base import serializers, filters, models
from base.vrp_extra import new_pragmatic_types as prg, config_types as cfg
from base.vrp_extra.utils import get_job, get_multi_job, get_vehicles, get_routing_matrix, \
    get_vehicle_profile_locations, get_job_locations, EnumRouteVehicleProfile, \
    get_jobs_arrival_time
import pandas as pd

config = cfg.Config(
    termination=cfg.Termination(
        maxTime=300,
        maxGenerations=3000
    )
)

paginator = LimitOffsetPagination()

paginator.default_limit = 10
paginator.default_offset = 0


@api_view(['POST'])
def work_post(request):
    if request.method == 'POST':
        serializer = serializers.WorkSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response({"message": "Hello, world!"})


@api_view(["PUT"])
def work_put(request, pk):
    work_instance = get_object_or_404(models.Work, pk=pk)
    if request.method == "PUT":
        serializer = serializers.WorkSerializer(work_instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def category_update(request, pk):
    category_ins = get_object_or_404(models.Category, pk=pk)
    if request.method == "PUT":
        serializer = serializers.CategorySerializer(category_ins, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def category_create(request):
    if request.method == "POST":
        serializer = serializers.CategorySerializer(data=request.data)
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


@api_view(["PUT"])
def job_put(request, pk):
    job_instance = get_object_or_404(models.Job, pk=pk)
    if request.method == "PUT":
        serializer = serializers.JobSerializer(job_instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def export_solution_csv(request, pk):
    if request.method == "GET":
        queryset_sol = models.Solution.objects.select_related('work').filter(id=pk).first()
        solution_pydantic = prg.Solution(**json.loads(queryset_sol.solution))
        solution_data = []
        for tour in solution_pydantic.tours:
            for stop in tour.stops:
                for activity in stop.activities:
                    arrival_time = activity.time.start if (activity.time and activity.time.start) else stop.time.arrival
                    departure_time = activity.time.end if (activity.time and activity.time.end) else stop.time.departure
                    solution_data.append({
                        'Vehicle ID': tour.vehicleId,
                        'Type': activity.type,
                        'Job': activity.jobId,
                        'Lattitude': stop.location.lat,
                        'Longitude': stop.location.lng,
                        'Arrival Time': datetime.fromisoformat(str(arrival_time)).astimezone(
                            timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S"),
                        'Departure Time': datetime.fromisoformat(str(departure_time)).astimezone(
                            timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S"),
                        'Load': stop.load[0],
                        'Distance': stop.distance / 1000,
                    })

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="solution.csv"'
        writer = csv.DictWriter(response, fieldnames=solution_data[0].keys())
        writer.writeheader()
        writer.writerows(solution_data)
        return response
    return None


def calculate_tkm(load: float, distance: float) -> float:
    """
    This will calculate tonne-km
    Formula: row_n = load_(n-1) * (distance_n - distance_(n-1))
    """
    # Example modification
    load = load * 2
    return load * distance


def calculate_emission(tkm: float, emission_intensity = 191) -> float:
    """
    This will calculate emission
    Formula: row_n = (emission_intensity * tkm)/1000
    """
    # Example modification
    return (emission_intensity * tkm)/1000


@api_view(["GET"])
def emission_estimation(request, pk):
    if request.method == "GET":
        export_to_csv = request.GET.get("export_to_csv")
        queryset_sol = models.Solution.objects.select_related('work').filter(id=pk).first()
        solution_pydantic = prg.Solution(**json.loads(queryset_sol.solution))
        solution_data = []
        for tour in solution_pydantic.tours:
            for stop in tour.stops:
                for activity in stop.activities:
                    arrival_time = activity.time.start if (activity.time and activity.time.start) else stop.time.arrival
                    departure_time = activity.time.end if (activity.time and activity.time.end) else stop.time.departure
                    solution_data.append({
                        'Vehicle ID': tour.vehicleId,
                        'Type': activity.type,
                        'Job': activity.jobId,
                        'Lattitude': stop.location.lat,
                        'Longitude': stop.location.lng,
                        'Arrival Time': datetime.fromisoformat(str(arrival_time)).astimezone(
                            timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S"),
                        'Departure Time': datetime.fromisoformat(str(departure_time)).astimezone(
                            timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S"),
                        'Load': stop.load[0],
                        'Distance': stop.distance,
                    })

        df = pd.DataFrame.from_records(solution_data)

        df["Distance"] = df["Distance"].apply(lambda x: x/1000)
        
        df["tkm"] = calculate_tkm(
            df["Load"].shift(1),
            df["Distance"] - df["Distance"].shift(1)
        )
        df["tkm"].fillna(0, inplace=True)
        df["emission"] = df["tkm"].apply(lambda x: calculate_emission(x))
        df = df[["Vehicle ID", "Job", "Load", "Distance", "tkm", "emission"]]
        if export_to_csv and export_to_csv.lower() == "true":
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="emission_solution.csv"'
            writer = csv.DictWriter(response, fieldnames=df.columns)
            writer.writeheader()
            writer.writerows(df.to_dict(orient="records"))
            return response

            # Default JSON response
        total_emission = float(df["emission"].sum())
        records = df.to_dict("records")
        return Response({
            "emission": total_emission,
            "records": records
        }, status=status.HTTP_200_OK)

    return None


@api_view(["GET"])
def previous_solution_get(request):
    if request.method == "GET":
        queryset_sol = models.Solution.objects.select_related('work').order_by(
            '-updated_at').last()
        if queryset_sol is None:
            return Response({}, status=status.HTTP_200_OK)
        queryset_fresh = models.FreshnessPenalty.objects.filter(solution=queryset_sol).first()
        serializer_solution = serializers.SolutionSerializer(queryset_sol).data
        serializer_jobs = serializers.FreshnessPenaltySerializer(queryset_fresh).data
        return Response({"id": serializer_solution.get("id", None), "solution":
            serializer_solution.get("solution", None), "jobs":
                             serializer_jobs.get("freshness_penalty", None),
                         "work": serializer_solution.get("work", None)})
    return None


@api_view(["GET"])
def job_get(request):
    if request.method == "GET":
        result = filters.WorkFilter(request.GET,
                                    queryset=models.Job.objects.select_related('work').all())
        paginated_queryset = paginator.paginate_queryset(result.qs, request)
        serializer = serializers.MultiJobSerializerGet(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
    return None


@api_view(["GET"])
def category_get(request):
    if request.method == "GET":
        result = filters.WorkFilter(request.GET,
                                    queryset=models.Category.objects.all())
        paginated_queryset = paginator.paginate_queryset(result.qs, request)
        serializer = serializers.CategorySerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
    return None


@api_view(["GET"])
def get_work(request):
    if request.method == "GET":
        result = filters.WorkFilter(request.GET, queryset=models.Work.objects \
                                    .prefetch_related('job_set') \
                                    .prefetch_related('vehicle_set').all())
        paginated_queryset = paginator.paginate_queryset(result.qs, request)
        serializer = serializers.WorkSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
    return None


@api_view(["GET"])
def get_search_work(request):
    if request.method == "GET":
        result = filters.WorkFilter(request.GET, queryset=models.Work.objects \
                                    .prefetch_related('job_set') \
                                    .prefetch_related('vehicle_set').all())
        serializer = serializers.WorkSerializer(result.qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return None


@api_view(["GET"])
def vehicle_get(request):
    if request.method == "GET":
        result = filters.WorkFilter(request.GET,
                                    queryset=models.Vehicle.objects.select_related("profile",
                                                                                   'work').all())
        paginated_queryset = paginator.paginate_queryset(result.qs, request)
        serializer = serializers.VehicleSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
    return None


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


@api_view(["POST"])
@transaction.atomic
def bulk_job_create(request):
    if request.method == "POST":
        serializer = serializers.BulkJobCreate(data=request.data)
        if serializer.is_valid(raise_exception=True):
            reader = csv.DictReader(
                io.StringIO(serializer.validated_data["file"].read().decode("utf-8-sig")))
            data = list(reader)
            work = serializer.validated_data["work_id"]
            serialize_data = [item | {"work_id": work.id} for item in data]
            job_serializer = serializers.JobSerializer(data=serialize_data,
                                                       many=True)

            if job_serializer.is_valid(raise_exception=True):
                job_serializer.save()

    return Response({"message": "Hello, world!"})


@api_view(["POST"])
@transaction.atomic
def bulk_fleet_create(request):
    if request.method == "POST":
        serializer = serializers.BulkJobCreate(data=request.data)
        if serializer.is_valid(raise_exception=True):
            reader = csv.DictReader(
                io.StringIO(serializer.validated_data["file"].read().decode("utf-8-sig")))
            data = list(reader)
            work = serializer.validated_data["work_id"]
            serialize_data = [item | {"work_id": work.id} for item in data]
            fleet_serializer = serializers.VehicleSerializer(data=serialize_data,
                                                             many=True)

            if fleet_serializer.is_valid(raise_exception=True):
                print(fleet_serializer.data)
                fleet_serializer.save()

    return Response({"message": "Hello, world!"})


@api_view(["DELETE"])
def job_delete(request, pk):
    result = get_object_or_404(models.Job, pk=pk)
    result.delete()
    return Response({"details": "ok"}, status=status.HTTP_202_ACCEPTED)


@api_view(["DELETE"])
def category_delete(request, pk):
    result = get_object_or_404(models.Category, pk=pk)
    result.delete()
    return Response({"details": "ok"}, status=status.HTTP_202_ACCEPTED)


@api_view(["DELETE"])
def delete_work(request, pk):
    result = get_object_or_404(models.Work, pk=pk)
    result.delete()
    return Response({"details": "ok"}, status=status.HTTP_202_ACCEPTED)


@api_view(["POST"])
def vehicle_bulk_post(request):
    if request.method == "POST":
        serializer = serializers.VehicleSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def vehicle_put(request, pk):
    if request.method == "PUT":
        vehicle = get_object_or_404(models.Vehicle, pk=pk)
        serializer = serializers.VehicleSerializer(vehicle, data=request.data)
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


@api_view(['PUT'])
def vehicle_profile_update(request, pk):
    old_profile = get_object_or_404(models.VehicleProfile, pk=pk)
    if request.method == 'PUT':
        serializer = serializers.VehicleProfileSerializer(old_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response({"message": "Hello, world!"})


@api_view(["GET"])
def vehicle_profile_get(request):
    if request.method == "GET":
        result = filters.WorkFilter(request.GET, queryset=models.VehicleProfile.objects \
                                    .prefetch_related('vehicle_set').all())
        paginated_queryset = paginator.paginate_queryset(result.qs, request)
        serializer = serializers.VehicleProfileSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
    return None


@api_view(["GET"])
def search_vehicle_profile(request):
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
    work = models.Work.objects.get(pk=pk)

    _jobs = models.Job.objects.select_related('category').filter(work_id=pk, multi=None)
    _multi_jobs = models.MultiJob.objects.filter(work_id=pk, job__isnull=False).distinct()

    # For Cost Penalty
    job_data_db = []

    jobs = [get_job(_job, job_data_db) for _job in _jobs]
    multi_jobs = [get_multi_job(_job, job_data_db) for _job in _multi_jobs]

    _vehicles = models.Vehicle.objects.select_related('profile').filter(work_id=pk)

    vehicles, profiles = get_vehicles(_vehicles)
    fleet = prg.Fleet(vehicles=vehicles,
                      profiles=[prg.RoutingProfile(name=profile) for profile in profiles])

    plan = prg.Plan(jobs=jobs + multi_jobs)
    problem = prg.Problem(plan=plan, fleet=fleet)

    # new work

    matrices = []
    custom_matrix = True

    if custom_matrix:
        v_locations = get_vehicle_profile_locations(fleet)
        j_locations = get_job_locations(plan)
        durations, distances = get_routing_matrix(j_locations + v_locations,
                                                  EnumRouteVehicleProfile.DRIVING_HGV)
        durations, distances = list(map(lambda x: int(x), durations)), list(
            map(lambda x: int(x), distances))
        matrix = prg.RoutingMatrix(
            profile='DRIVING_HGV',
            durations=durations,
            distances=distances
        )
        matrices.append(matrix.model_dump_json())
    solution = prg.Solution(**json.loads(vrp_cli.solve_pragmatic(
        problem=problem.model_dump_json(),
        matrices=matrices,
        config=config.model_dump_json(),
    )))

    jobs_arrival_time = get_jobs_arrival_time(solution)

    job_serialized_data = serializers.JobSerializerWithFreshnessPenalty(job_data_db,
                                                                        many=True).data
    for job in job_serialized_data:
        arrival_time = jobs_arrival_time.get(job['id'], None)
        if arrival_time is None:
            continue
        job['arrival_time'] = arrival_time
        if job['start_at'] and job['category']:
            time_difference = arrival_time - datetime.fromisoformat(
                job['start_at'].replace("Z", "+00:00"))
            hours_difference = math.fabs(time_difference.total_seconds()) / 3600
            job["f_penalty"] = job['category']['penalty'] * hours_difference

    work_serializer = serializers.WorkSerializer(work)
    vehicle_serializer = serializers.VehicleSerializer(_vehicles, many=True)
    solution_data = solution.model_dump_json()

    # Crucial for last solution
    job_json_data = DjangoJSONEncoder().encode(job_serialized_data)
    _solution = models.Solution.objects.filter(work=work).first()
    if _solution:
        _solution.solution = solution_data
        _solution.save()
    else:
        _solution = models.Solution.objects.create(solution=solution_data, work=work)

    _freshness_penalty = models.FreshnessPenalty.objects.filter(solution=_solution).first()
    if _freshness_penalty:
        _freshness_penalty.freshness_penalty = job_json_data
        _freshness_penalty.save()
    else:
        models.FreshnessPenalty.objects.create(freshness_penalty=job_json_data,
                                               solution=_solution)

    context = {
        "id": _solution.id,
        "solution": solution.model_dump(),
        "work": work_serializer.data,
        "jobs": job_serialized_data,
        "vehicles": vehicle_serializer.data,

    }
    return Response(context, status=status.HTTP_202_ACCEPTED)
