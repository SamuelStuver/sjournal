pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh 'curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash'
        sh 'exec $SHELL'
        sh 'pyenv --version'
        sh 'pyenv update'
      }
    }

  }
}