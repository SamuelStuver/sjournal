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
            }
        }
        stage('Test') {
            steps {
                // Run Tests
                sh 'docker run sjournal-docker'

            }
        }
    }
    post {
        always {
            // Compile reports
            //DOCKER_ID=${docker ps --latest --quiet}
            script {
                LATEST_DOCKER_ID = "(docker ps --latest --quiet)"
            }
            sh "mkdir -p reports"
            sh "docker cp ${LATEST_DOCKER_ID}:app/reports/report.html ./reports"
            sh "docker cp ${LATEST_DOCKER_ID}:app/reports/report.xml ./reports"
            //sh "docker cp ${LATEST_DOCKER_ID}:app/reports/test_log.log ./reports"
            sh "pwd"
            sh "ls"
            // Remove all exited containers
            sh "docker ps -a -q -f status=exited | xargs docker rm"
        }
        failure {
            sh "echo Reached Failure Step"
        }
    }
}