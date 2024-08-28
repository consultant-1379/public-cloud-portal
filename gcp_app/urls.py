from django.urls import path
from . import views

urlpatterns = [
   path('', views.index, name="index"),
   path('start_instance', views.view_start_instance, name='start_instance'),
   path('stop_instance', views.view_stop_instance, name='stop_instance'),
   path('project_instances', views.get_project_instances, name='project_instances'),
   path('project_instances/<str:project_id>', views.view_gcp_project_instances, name='view_project_instances'),
]