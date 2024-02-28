from django.urls import path
from . import views, rest_views

urlpatterns = [
    path('', views.work, name="home"),
    path('works/', rest_views.get_work, name="work-get"),
    path('solve/<int:pk>', rest_views.solve, name="work-solve"),
    path('work-create/', rest_views.work_post, name="work-post"),
    path('work_delete/<int:pk>/', rest_views.delete_work, name="work-delete"),
    path('job/', views.job, name='job'),
    path('job-create/', rest_views.job_post, name='job-create'),
    path('job-delete/<int:pk>/', rest_views.job_delete, name='job-delete'),
    path('jobs/', rest_views.job_get, name='job-get'),
    path('multijob/', views.multi_job, name='multijob'),
    path('multijob-create/', rest_views.multi_job_post, name='multijob-create'),
    path('vehicle/', views.vehicle, name='vehicle'),
    path('vehicles/', rest_views.vehicle_get, name='vehicle-get'),
    path('vehicle-create/', rest_views.vehicle_bulk_post, name='vehicle-create'),
    path('vehicle-delete/<int:pk>/', rest_views.vehicle_delete, name="vehicle-delete"),
    path('vehicle-profile-create/', rest_views.vehicle_profile_post, name='vehicle-profile-create'),
    path('vehicle-profile-delete/<int:pk>/', rest_views.delete_vehicle_profile, name="vehicle-profile-delete"),
    path('vehicle-profiles/', rest_views.vehicle_profile_get, name='vehicle-profile-get'),
    path('solution/<int:pk>', views.solution, name='solution'),
    path('solution/<int:pk>/solve', views.solve, name='solve'),
]
