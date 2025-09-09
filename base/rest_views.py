import csv
import io
import json
import math
from datetime import datetime

import numpy as np
import pandas as pd
import vrp_cli
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction, IntegrityError
from django.db.models import Count
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

config = cfg.Config(
    termination=cfg.Termination(
        maxTime=300,
        maxGenerations=3000
    )
)

paginator = LimitOffsetPagination()

paginator.default_limit = 10
paginator.default_offset = 0

#
# @api_view(['POST'])
# def work_post(request):
#     if request.method == 'POST':
#         serializer = serializers.WorkSerializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response({"message": "Hello, world!"})
#
#
# @api_view(["PUT"])
# def work_put(request, pk):
#     work_instance = get_object_or_404(models.Work, pk=pk, created_by=request.user)
#     if request.method == "PUT":
#         serializer = serializers.WorkSerializer(work_instance, data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#     return Response({"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(["PUT"])
# def category_update(request, pk):
#     category_ins = get_object_or_404(models.Category, pk=pk, created_by=request.user)
#     if request.method == "PUT":
#         serializer = serializers.CategorySerializer(category_ins, data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#     return Response({"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(["POST"])
# def category_create(request):
#     if request.method == "POST":
#         serializer = serializers.CategorySerializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response({"message": "Hello, world!"})
#



@api_view(['POST'])
def work_post(request):
    """Create a new Work object"""
    serializer = serializers.WorkSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        try:
            serializer.save()
            return Response(
                {"message": "Work created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        except IntegrityError:
            return Response(
                {"error": "A work with this name already exists for the current user."},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def work_put(request, pk):
    """Update an existing Work object"""
    work_instance = get_object_or_404(models.Work, pk=pk, created_by=request.user)
    serializer = serializers.WorkSerializer(work_instance, data=request.data, context={"request": request})
    if serializer.is_valid():
        try:
            serializer.save()
            return Response(
                {"message": "Work updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        except IntegrityError:
            return Response(
                {"error": "A work with this name already exists for the current user."},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def category_update(request, pk):
    """Update an existing Category object"""
    category_ins = get_object_or_404(models.Category, pk=pk, created_by=request.user)
    serializer = serializers.CategorySerializer(category_ins, data=request.data, context={"request": request})
    if serializer.is_valid():
        try:
            serializer.save()
            return Response(
                {"message": "Category updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        except IntegrityError:
            return Response(
                {"error": "A category with this name already exists for the current user."},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def category_create(request):
    """Create a new Category object"""
    serializer = serializers.CategorySerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        try:
            serializer.save()
            return Response(
                {"message": "Category created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        except IntegrityError:
            return Response(
                {"error": "A category with this name already exists for the current user."},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    job_instance = get_object_or_404(models.Job, pk=pk, created_by=request.user)
    if request.method == "PUT":
        serializer = serializers.JobSerializer(job_instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def export_solution_csv(request, pk):
    if request.method == "GET":
        queryset_sol = models.Solution.objects.select_related('work').filter(id=pk,
                                                                             work__created_by=request.user).first()
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


@api_view(["GET"])
def emission_estimation(request, pk):
    """
    Output columns (same row order as solution CSV, one row per activity):
      Vehicle Name | Job | Load | Distance | Emission (kg)

    Emission per row n:
      segment_km = Distance(n) - Distance(n-1)   [per vehicle]
      EF bucket uses previous row’s load% (ef(n-1)):
         load% = prev_load_cnt / max_capacity
         exactly 0/50/100 -> that bucket; otherwise -> 'avg'
      Emission(kg) = segment_km * EF(bucket)
    """
    export_to_csv = (request.GET.get("export_to_csv") or "").lower() == "true"

    # --- 1) Load solution ---
    sol = models.Solution.objects.select_related('work').filter(id=pk, work__created_by=request.user).first()
    if not sol:
        return Response({"detail": "Solution not found."}, status=status.HTTP_404_NOT_FOUND)

    solution = prg.Solution(**json.loads(sol.solution))

    # --- 2) Build per-activity rows ---
    rows = []
    for tour in solution.tours:
        vehicle_key = str(tour.vehicleId)
        for stop in tour.stops:
            for activity in stop.activities:
                job_value = getattr(activity, "jobId", None) or getattr(activity, "type", None)
                rows.append({
                    "Vehicle Name": vehicle_key,
                    "Job": job_value,
                    "Load": int(stop.load[0]) if (stop.load and len(stop.load)) else 0,
                    "Distance": float(stop.distance or 0.0) / 1000.0,  # km
                    "_vehicle_key": vehicle_key,
                })

    if not rows:
        if export_to_csv:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="emission_solution.csv"'
            writer = csv.DictWriter(
                response,
                fieldnames=["Vehicle Name", "Job", "Load", "Distance", "Load%", "EF (kg/km)", "Emission (kg)"]
            )
            writer.writeheader()
            return response
        return Response({"total_emission_kg": 0.0, "records": []}, status=status.HTTP_200_OK)

    df = pd.DataFrame.from_records(rows)

    # --- 3) Join vehicle profiles (EF needs truck_type, temperature, max_capacity) ---
    qs = models.Vehicle.objects.select_related('profile').filter(work=sol.work)
    vehicles_by_id = {str(v.id): v for v in qs}
    vehicles_by_name = {v.name: v for v in qs}

    prof_map = {}
    missing_keys = []
    for key in df["_vehicle_key"].unique():
        v = vehicles_by_id.get(key) or vehicles_by_name.get(key)
        if not v:
            missing_keys.append(key)
            continue
        prof = v.profile
        prof_map[key] = {
            "_truck_type": prof.truck_type,
            "_temperature": prof.temperature,
            "_max_capacity": int(prof.max_capacity or 0),
        }

    if missing_keys:
        return Response(
            {"detail": "Vehicle(s) not found in DB for emission factors.",
             "vehicles": missing_keys},
            status=status.HTTP_400_BAD_REQUEST
        )

    df["_truck_type"] = df["_vehicle_key"].map(lambda k: prof_map[k]["_truck_type"])
    df["_temperature"] = df["_vehicle_key"].map(lambda k: prof_map[k]["_temperature"])
    df["_max_capacity"] = df["_vehicle_key"].map(lambda k: prof_map[k]["_max_capacity"])

    if (df["_max_capacity"] <= 0).any():
        bad = df.loc[df["_max_capacity"] <= 0, "_vehicle_key"].unique().tolist()
        return Response(
            {"detail": "Invalid max_capacity (<=0) for vehicle(s).", "vehicles": bad},
            status=status.HTTP_400_BAD_REQUEST
        )

    # --- 4) Segment distance & previous load per vehicle ---
    df["_prev_distance"] = (
        df.groupby("_vehicle_key", sort=False)["Distance"]
        .shift(1)
        .fillna(df["Distance"])  # first row per vehicle -> segment 0
    )
    df["_segment_km"] = (df["Distance"] - df["_prev_distance"]).clip(lower=0.0)

    df["_prev_load"] = (
        df.groupby("_vehicle_key", sort=False)["Load"]
        .shift(1)
        .fillna(df["Load"])  # EF doesn't matter on first row (segment 0)
    )

    # --- 5) Bucket selection (exact 0/50/100 else 'avg') ---
    prev_load_int = df["_prev_load"].astype("int64")
    max_cap_int = df["_max_capacity"].astype("int64")
    is0 = prev_load_int == 0
    is100 = prev_load_int == max_cap_int
    is50 = (prev_load_int * 2) == max_cap_int

    # Use strings for buckets to avoid dtype issues when merging with 'avg'
    df["_bucket"] = np.where(is0, "0",
                             np.where(is100, "100",
                                      np.where(is50, "50", "avg")))

    # Also compute percentage (for CSV)
    df["_load_pct"] = (prev_load_int * 100.0 / max_cap_int.where(max_cap_int != 0, 1))

    # --- 6) Emission factors ---
    EF = {
        ('rigid_3_5_7_5', 'ambient'): {0: 0.46138, 50: 0.50103, 100: 0.54068, 'avg': 0.49548},
        ('rigid_7_5_17', 'ambient'): {0: 0.55061, 50: 0.62832, 100: 0.70603, 'avg': 0.60501},
        ('rigid_17_plus', 'ambient'): {0: 0.77400, 50: 0.94152, 100: 1.10905, 'avg': 0.99156},
        ('artic_3_5_33', 'ambient'): {0: 0.62775, 50: 0.78163, 100: 0.93552, 'avg': 0.78471},
        ('artic_33_plus', 'ambient'): {0: 0.64734, 50: 0.85827, 100: 1.06921, 'avg': 0.93421},

        ('rigid_3_5_7_5', 'refrigerated'): {0: 0.54937, 50: 0.59667, 100: 0.64397, 'avg': 0.59005},
        ('rigid_7_5_17', 'refrigerated'): {0: 0.65559, 50: 0.74830, 100: 0.84101, 'avg': 0.72049},
        ('rigid_17_plus', 'refrigerated'): {0: 0.92128, 50: 1.12114, 100: 1.32100, 'avg': 1.18083},
        ('artic_3_5_33', 'refrigerated'): {0: 0.72566, 50: 0.90403, 100: 1.08239, 'avg': 0.90759},
        ('artic_33_plus', 'refrigerated'): {0: 0.74800, 50: 0.99249, 100: 1.23699, 'avg': 1.08051},
    }

    ef_rows = []
    for (tt, temp), vals in EF.items():
        for bucket, ef in vals.items():
            bucket_key = "avg" if bucket == "avg" else str(bucket)  # normalize to string
            ef_rows.append({
                "_truck_type": tt,
                "_temperature": temp,
                "_bucket": bucket_key,
                "_ef_kg_per_km": float(ef),
            })
    EF_LUT = pd.DataFrame(ef_rows)

    df = df.merge(EF_LUT, on=["_truck_type", "_temperature", "_bucket"], how="left")
    if df["_ef_kg_per_km"].isna().any():
        missing = df[df["_ef_kg_per_km"].isna()][["_truck_type", "_temperature", "_bucket"]].drop_duplicates()
        return Response(
            {"detail": "Missing emission factor mapping", "missing": missing.to_dict("records")},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # --- 7) Emission calculation ---
    df["Emission (kg)"] = df["_segment_km"] * df["_ef_kg_per_km"]

    # JSON for dashboard
    json_cols = ["Vehicle Name", "Job", "Load", "Distance", "Emission (kg)"]
    out_json = df[json_cols].copy()
    total_emission = float(out_json["Emission (kg)"].sum())

    if export_to_csv:
        df["_load_pct"] = df["_load_pct"].round(2)
        df["_ef_kg_per_km"] = df["_ef_kg_per_km"].round(5)
        csv_cols = ["Vehicle Name", "Job", "Load", "Distance", "Load%", "EF (kg/km)", "Emission (kg)"]
        out_csv = pd.DataFrame({
            "Vehicle Name": df["Vehicle Name"],
            "Job": df["Job"],
            "Load": df["Load"],
            "Distance": df["Distance"].round(6),
            "Load%": df["_load_pct"],
            "EF (kg/km)": df["_ef_kg_per_km"],
            "Emission (kg)": df["Emission (kg)"].round(6),
        })

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="emission_solution.csv"'
        writer = csv.DictWriter(response, fieldnames=csv_cols)
        writer.writeheader()
        writer.writerows(out_csv.to_dict(orient="records"))
        return response

    return Response({
        "total_emission_kg": round(total_emission, 6),
        "records": out_json.round({"Distance": 6, "Emission (kg)": 6}).to_dict(orient="records"),
    }, status=status.HTTP_200_OK)


@api_view(["GET"])
def previous_solution_get(request):
    if request.method == "GET":
        queryset_sol = models.Solution.objects.select_related('work').order_by(
            '-updated_at').filter(work__created_by=request.user).last()
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
                                    queryset=models.Job.objects.select_related('work').filter(
                                        created_by=request.user).all())
        paginated_queryset = paginator.paginate_queryset(result.qs, request)
        serializer = serializers.MultiJobSerializerGet(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
    return None


@api_view(["GET"])
def category_get(request):
    if request.method == "GET":
        result = filters.WorkFilter(request.GET,
                                    queryset=models.Category.objects.filter(created_by=request.user).all())
        paginated_queryset = paginator.paginate_queryset(result.qs, request)
        serializer = serializers.CategorySerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
    return None


@api_view(["GET"])
def get_work(request):
    if request.method == "GET":
        result = filters.WorkFilter(request.GET, queryset=models.Work.objects \
                                    .prefetch_related('job_set') \
                                    .prefetch_related('vehicle_set').filter(created_by=request.user).all())
        paginated_queryset = paginator.paginate_queryset(result.qs, request)
        serializer = serializers.WorkSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
    return None


@api_view(["GET"])
def get_search_work(request):
    if request.method == "GET":
        result = filters.WorkFilter(request.GET, queryset=models.Work.objects \
                                    .prefetch_related('job_set') \
                                    .prefetch_related('vehicle_set').filter(created_by=request.user).all())
        serializer = serializers.WorkSerializer(result.qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return None


@api_view(["GET"])
def vehicle_get(request):
    if request.method == "GET":
        result = filters.WorkFilter(request.GET,
                                    queryset=models.Vehicle.objects.select_related("profile",
                                                                                   'work').filter(
                                        created_by=request.user).all())
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
    result = get_object_or_404(models.Job, pk=pk, created_by=request.user)
    result.delete()
    return Response({"details": "ok"}, status=status.HTTP_202_ACCEPTED)


@api_view(["DELETE"])
def category_delete(request, pk):
    result = get_object_or_404(models.Category, pk=pk)
    result.delete()
    return Response({"details": "ok"}, status=status.HTTP_202_ACCEPTED)


@api_view(["DELETE"])
def delete_work(request, pk):
    result = get_object_or_404(models.Work, pk=pk, created_by=request.user)
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
        vehicle = get_object_or_404(models.Vehicle, pk=pk, created_by=request.user)
        serializer = serializers.VehicleSerializer(vehicle, data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def vehicle_delete(request, pk):
    result = get_object_or_404(models.Vehicle, pk=pk, created_by=request.user)
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
    old_profile = get_object_or_404(models.VehicleProfile, pk=pk, created_by=request.user)
    if request.method == 'PUT':
        serializer = serializers.VehicleProfileSerializer(old_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response({"message": "Hello, world!"})


@api_view(["GET"])
def vehicle_profile_get(request):
    if request.method == "GET":
        qs = (models.VehicleProfile.objects
              .annotate(total_vehicles=Count("vehicle"))  # <-- annotate by reverse FK
              .prefetch_related("vehicle_set").filter(created_by=request.user).all())
        result = filters.WorkFilter(request.GET, queryset=qs)
        paginated = paginator.paginate_queryset(result.qs, request)
        serializer = serializers.VehicleProfileSerializer(paginated, many=True)
        return paginator.get_paginated_response(serializer.data)
    return None


@api_view(["GET"])
def search_vehicle_profile(request):
    qs = (models.VehicleProfile.objects
          .annotate(total_vehicles=Count("vehicle"))
          .prefetch_related("vehicle_set").filter(created_by=request.user).all())
    result = filters.WorkFilter(request.GET, queryset=qs)
    serializer = serializers.VehicleProfileSerializer(result.qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_vehicle_profile(request, pk):
    result = get_object_or_404(models.VehicleProfile, pk=pk, created_by=request.user)
    result.delete()
    return Response({"details": "ok"}, status=status.HTTP_202_ACCEPTED)


@api_view(["GET"])
def solve(request, pk):
    work = models.Work.objects.get(pk=pk, created_by=request.user)

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
