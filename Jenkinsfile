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
                sh "docker build -t sjournal-docker ."
                sh "echo BUILT DOCKER IMAGE"
                sh "ls"
                sh "docker images"
            }
        }
        stage('Test') {
            steps {
                sh 'docker run sjournal-docker'
            }
        }
        stage('Compile Reports') {
            steps {
                sh "mkdir reports"
                sh "docker cp sjournal-docker:./reports/report.html ./reports"
                sh "docker cp sjournal-docker:./reports/report.xml ./reports"
                sh "docker cp sjournal-docker:./reports/test_log.log ./reports"
                sh "pwd"
                sh "ls"
            }
        }
    }
    post {
        always {
            script {
                sh "docker stop sjournal-docker"
                sh "docker cp sjournal-docker:app ./logs"
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