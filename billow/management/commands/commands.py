from django.core.management.base import BaseCommand
from django.utils import timezone
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.mgmt.consumption import ConsumptionManagementClient
from datetime import datetime, timedelta
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.compute import ComputeManagementClient
from billow.models import *
import hashlib
from azure_app.azure_utils import azure_daily_snapshot, get_index
from aws_app.aws_utils import aws_daily_snapshot
from gcp_app.gcp_utils import gcp_daily_snapshot
from billow.billow_utils import *


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

     snap_index = get_index()
     snap_index_snapshot = get_index_snapshot()
     azure_instance_snapshot(snap_index_snapshot)
     gcp_instance_snapshot(snap_index_snapshot)
     aws_instance_snapshot(snap_index_snapshot)

     aws_daily_snapshot(snap_index)
     gcp_daily_snapshot(snap_index)
     azure_daily_snapshot(snap_index)