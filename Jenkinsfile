pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'sudo apt-get install python3.9'
                sh 'pip install -r requirements.txt'
                sh 'cd publish'
                sh 'sh ./publish_local.sh'
            }
        }
        stage('Test') {
            steps {
                sh 'pwd'
            }
        }
        stage('Cleanup') {
            steps {
                sh 'pip uninstall -r requirements.txt -y'
                sh 'pip uninstall sjournal'
            }
        }
    }
}