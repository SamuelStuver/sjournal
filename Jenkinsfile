pipeline {
    agent any
    stages {
        stage('Build') {
            agent { dockerfile true }
            steps {
                sh 'ls'
                sh 'pwd'
                sh 'whoami'
            }
        }
    }
}