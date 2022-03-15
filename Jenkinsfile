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
                // sh "sudo apt-get install tk -y"
                sh "docker build -t sjournal-docker ."
                sh "echo BUILT DOCKER IMAGE"
                sh "ls"
                sh "docker images"
            }
        }
        stage('Test') {
            steps {
                sh 'docker run -e DISPLAY=host.docker.internal:0 sjournal-docker'
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
                sh "docker ps -a -q -f status=exited | xargs docker rm"
            }
            deleteDir()
        }
        failure {
            sh "echo Reached Failure Step"
        }
    }
}