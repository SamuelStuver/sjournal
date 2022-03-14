pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh 'pwd'
        sh 'whoami'
        withEnv(['PYENV_ROOT="$HOME/.pyenv"', 'PATH="$PYENV_ROOT/bin:$PATH"']) {
            sh 'pyenv --version'
            sh 'pyenv update'
        }
      }
    }

  }
}