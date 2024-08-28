from django.urls import path
from . import views

urlpatterns = [
    path('aws_total_cost/', views.aws_total_cost, name='aws_total_cost'),
]