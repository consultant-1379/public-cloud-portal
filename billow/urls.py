from django.urls import path
from django.contrib.auth import views as auth_views
from . import views #go to current directory and grab views from there


app_name = 'billow'


urlpatterns = [
    path('index/', views.index_billow, name="index"),
    path('login/', auth_views.LoginView.as_view(template_name = "login.html"),name='login'), #default view
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('billow_get_bill', views.billow_get_bill, name='billow_get_bill'),
    path('billow_bill', views.billow_bill, name='billow_bill'),
    path('instance_action', views.instance_action, name='instance_action'),
    path('manage_instances', views.manage_instances, name='manage_instances'),
    path('create_instances', views.create_instances, name='create_instances'),
    path('create_gcp_instance/', views.create_gcp_instance, name='create_gcp_instance'),
    path('create_gcp_instance_form/', views.create_gcp_instance_form, name='create_gcp_instance_form'),
    path('create_aws_instance_form/', views.create_aws_instance_form, name='create_aws_instance_form'),
    path('create_aws_instance',views.create_aws_instance, name='create_aws_instance'),
    path('create_azure_instance_form/', views.create_azure_instance_form, name='create_azure_instance_form'),
    path('create_azure_instance', views.create_azure_instance, name='create_azure_instance'),
    path('graph_landing_page', views.graph_landing_page, name='graph_landing_page'),
    path('graph_cost', views.graph_cost, name='graph_cost'),
    path('graph_resources', views.graph_resources, name='graph_resources'),
    path('start_all_instances', views.start_all_instances, name='start_all_instances'),
    path('stop_all_instances', views.stop_all_instances, name='stop_all_instances'),
    path('project_inventory', views.project_inventory, name='project_inventory'),
    path('program_graph_cost/<str:provider_name>/', views.program_graph_cost, name='program_graph_cost'),
    path('program_resource_graph/<str:provider_name>/', views.program_resource_graph, name='program_resource_graph'),

]