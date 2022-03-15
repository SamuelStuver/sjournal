pipeline {
    agent any
    environment {
    DOCKER_BUILDKIT=1
    }
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    stages {
        stage('Build') {
            steps {
                sh "docker build . -t sjournal_docker"
            }
        }
        stage('Test') {
            steps {
                sh 'docker run -d sjournal_docker'
            }
        }
        stage('Compile Reports') {
            steps {
                sh 'pip uninstall -r requirements.txt -y'
                sh 'pip uninstall sjournal'
            }
        }
    }
    post {
        always {
            script {
                sh "docker stop sjournal_docker"
                sh "docker cp sjournal_docker:app ./logs"
                sh "pwd"
                sh "ls"
            }
            deleteDir()
        }
        failure {
            sh "echo Reached Failure Step"
        }
    }
}