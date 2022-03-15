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
                sh "echo BUILT DOCKER IMAGE"
                sh "ls"
            }
        }
        stage('Test') {
            steps {
                sh 'docker run -d sjournal_docker'
            }
        }
        stage('Compile Reports') {
            steps {

                sh "docker cp sjournal_docker:app ./logs"

                sh "pwd"
                sh "ls"
            }
        }
    }
    post {
        always {
            script {
                sh "docker stop sjournal_docker"
                sh "docker cp sjournal_docker:app ./logs"
                sh "docker stop sjournal_docker"
                sh "docker rm sjournal_docker"
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