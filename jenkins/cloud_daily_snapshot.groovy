pipeline {
    agent {
        label 'billow_dev'
    }
    stages {
        stage('Get Cloud Daily Snapshots') {
            steps {
                    sh "/opt/jupyterhub/bin/python /home/eaoicop/repos/public-cloud-portal/manage.py commands"
            }
        }
	}
}

