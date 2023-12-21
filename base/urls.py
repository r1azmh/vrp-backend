from django.urls import path
from . import views

urlpatterns = [
    path('', views.work, name="home"),
    path('job/', views.job, name='job'),
    path('multijob/', views.multi_job, name='multijob'),
    path('vehicle/', views.vehicle, name='vehicle'),
    path('solution/<int:pk>', views.solution, name='solution'),
    path('solution/<int:pk>/solve', views.solve, name='solve'),
]
