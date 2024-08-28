from django.core.management.base import BaseCommand
from billow.models import *
from azure_app.azure_utils import start_vm
from aws_app.aws_utils import stop_instance_aws
from billow.views import stop_all_instances
from gcp_app.gcp_utils import stop_instance
from billow.billow_utils import *

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Start all instances'

    def handle(self, *args, **kwargs):
        gcp_instances = Gcp_instance.objects.all()
        for instance in gcp_instances:
            zone = str(Zone.objects.get(zone = instance.zone))
            instance_name = instance.instance_name
            instance.status = "Stopped"
            instance.save()
            stop_instance(instance.project, zone, instance_name, 'admin')
            logger.info('By User Admin || GCP Instance Stopped {}'.format(instance.instance_name))

        # Stop Azure instances
        azure_instances = Azure_instance.objects.all()
        for instance in azure_instances:
            resource_group = instance.resource_group_name
            instance_name = instance.instance_name
            instance.status = "Stopped"
            instance.save()
            start_vm(resource_group, instance_name)
            logger.info('By User Admin || Azure Instance Stopped {}'.format(instance.instance_name))

        # Stop AWS instances
        aws_instances = aws_instance.objects.all()
        for instance in aws_instances:
            instance_id = instance.instance_id
            if aws_instance.objects.filter(instance_id=instance_id).exists():
                try:
                    stop_instance_aws(instance_id)
                    instance.status = 'Stopped'
                    instance.save()
                    logger.info('By User Admin || AWS Instance Stopped {}'.format(instance_id))
                except Exception as e:
                    logger.info('By User Admin || AWS instance {} failed to stop'.format(instance_id))

        self.stdout.write(self.style.SUCCESS('Successfully stopped all instances.'))