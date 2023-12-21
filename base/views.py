# views.py
import json

import vrp_cli
from django.db import IntegrityError, transaction
from django.shortcuts import render
from pydantic.json import pydantic_encoder

from . import models, forms
from .vrp_extra import pragmatic_types as prg, config_types as cfg
from .vrp_extra.utils import get_job, get_vehicles, get_multi_job

# Create your views here.

config = cfg.Config(
    termination=cfg.Termination(
        maxTime=5,
        maxGenerations=1000
    )
)


def solve(request, pk):
    # data = dict()
    work = models.Work.objects.get(pk=pk)

    _jobs = models.Job.objects.filter(work_id=pk, multi=None)
    _multi_jobs = models.MultiJob.objects.filter(work_id=pk)
    jobs = [get_job(_job) for _job in _jobs]
    multi_jobs = [get_multi_job(_job) for _job in _multi_jobs]

    _vehicles = models.Vehicle.objects.select_related('type', 'profile').filter(work_id=pk)

    vehicles, profiles = get_vehicles(_vehicles)
    fleet = prg.Fleet(vehicles=vehicles,
                      profiles=[prg.RoutingProfile(name=profile) for profile in profiles])

    problem = prg.Problem(plan=prg.Plan(jobs=jobs + multi_jobs), fleet=fleet)
    solution = prg.Solution(**json.loads(vrp_cli.solve_pragmatic(
        problem=json.dumps(problem, default=pydantic_encoder),
        matrices=[],
        config=json.dumps(config, default=pydantic_encoder),
    )))

    # return JsonResponse(
    #     {"data": [job.model_dump() for job in jobs], "problem": problem.model_dump(), "fleet": fleet.model_dump(),
    #      "solution": solution.model_dump()})
    context = {
        "title": 'solution',
        "solution": solution.model_dump(),
        "work": work,
        "jobs": _jobs,
        "vehicles": _vehicles,

    }
    return render(request, 'base/solvePage.html', context=context)


def solution(request, pk):
    work = models.Work.objects.get(pk=pk)
    vehicles = models.Vehicle.objects.filter(work_id=pk)
    jobs = models.Job.objects.filter(work_id=pk)
    context = {
        "title": 'Solution',
        "work": work,
        "vehicles": vehicles,
        "jobs": jobs
    }
    return render(request, 'base/solution.html', context=context)


def work(request):
    if request.method == "POST":
        name = request.POST.get('work_name')
        models.Work.objects.create(
            name=name
        )
    works = models.Work.objects.all()
    context = {"works": works, "title": "Home"}
    return render(request, 'base/work.html', context=context)


def job(request):
    errors = {}
    if request.method == 'POST':
        form_data = forms.JobForm(request.POST)
        if form_data.is_valid():
            form_data.save(commit=True)
        else:
            errors = json.loads(form_data.errors.as_json())
    jobs = models.Job.objects.all()
    works = models.Work.objects.all()
    context = {"jobs": jobs, "work": works, "title": 'Job', "errors": errors}
    return render(request, 'base/job.html', context=context)


def vehicle(request):
    errors = {}
    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle_id')
        vehicle_location_lan = request.POST.get('vehicle_location_lan')
        vehicle_location_lat = request.POST.get('vehicle_duration_lat')
        capacity = request.POST.get('vehicle_capacity')
        vehicle_start_at = request.POST.get('vehicle_start_at')
        vehicle_end_at = request.POST.get('vehicle_end_at')
        vehicle_type_id = request.POST.get('vehicle_type_id')
        vehicle_profile_id = request.POST.get('vehicle_profile_id')
        vehicle_work_id = request.POST.get('vehicle_work_id')

        models.Vehicle.objects.create(
            name=vehicle_id,
            lat=vehicle_location_lat,
            lan=vehicle_location_lan,
            capacity=capacity,
            start_at=vehicle_start_at,
            end_at=vehicle_end_at,
            profile_id=vehicle_profile_id,
            work_id=vehicle_work_id,
            type_id=vehicle_type_id
        )
    vehicles = models.Vehicle.objects.all()
    profiles = models.VehicleProfile.objects.select_related('type').all()
    vehicle_types = models.VehicleType.objects.all()
    works = models.Work.objects.all()
    context = {
        "title": "Vehicle",
        "vehicles": vehicles,
        "types": vehicle_types,
        "works": works,
        "profiles": profiles,
        "errors": errors
    }
    return render(request, 'base/vehicle.html', context=context)


@transaction.atomic
def multi_job(request):
    if request.method == 'POST':
        multijob = forms.MultiJobForm(request.POST).save(commit=False)
        form_data1 = forms.JobForm(request.POST, prefix='job1')
        form_data2 = forms.JobForm(request.POST, prefix='job2')
        print(json.loads(form_data1.errors.as_json()))
        print(json.loads(form_data2.errors.as_json()))

        new_job1 = form_data1.save(commit=False)
        new_job2 = form_data2.save(commit=False)
        try:
            with transaction.atomic():
                _multi_job = multijob.save()
                new_job1.multi = multijob
                new_job2.multi = multijob
                new_job1.work = multijob.work
                new_job2.work = multijob.work
                new_job1.save()
                new_job2.save()
        except IntegrityError:
            transaction.rollback()
    jobs = models.Job.objects.all()
    works = models.Work.objects.all()
    job1_form = forms.JobForm(prefix='job1')
    context = {"jobs": jobs, "work": works, "title": 'Job', "job1_form": job1_form}
    return render(request, 'base/multijob.html', context=context)
