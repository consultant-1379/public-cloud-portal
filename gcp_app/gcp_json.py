from billow.models import *
import json
import os

gcp_obj = Cloud_Account.objects.filter(cloud_details__cloud_name="GCP")

def instances():
    for acc in gcp_obj:
        gcp_auth = Cloud_Provider.objects.get(cloud_name="GCP")
        cred = {
            "type": acc.username,
            "project_id": acc.project_id,
            "private_key_id": acc.token,
            "private_key": acc.secret_token.replace("\\n", "\n"),
            "client_email": acc.user_email,
            "client_id": acc.client_id,
            "auth_url": gcp_auth.auth_url,
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/{}%40local-shoreline-386208.iam.gserviceaccount.com".format(acc.subscription_id),
            "universe_domain": "googleapis.com"
        }

        directory = '/var/tmp'
        filename = '{}_{}.json'.format(acc.project_id, acc.subscription_id)
        filepath = os.path.join(directory, filename)

        with open(filepath, 'w') as outfile:
            json.dump(cred, outfile, indent=2)

    return filepath
