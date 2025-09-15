pipeline {
  agent any

  options {
    timestamps()
  }

  triggers {
    pollSCM('H/2 * * * * ')
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        sh 'git log -1 --oneline || true'
      }
    }

    stage('Build') {
      steps {
        sh '''
          echo ">>> Build step"
          if [ -f Makefile ]; then
            make build
          else
            echo "No Makefile; simulating build..."
            sleep 1
          fi
        '''
      }
    }

    stage('Test') {
      steps {
        sh '''
          echo ">>> Test step"
          if [ -f Makefile ]; then
            make test
          else
            echo "No tests yet; simulating tests..."
            echo "<testsuite name=\\"dummy\\"><testcase name=\\"ok\\"/></testsuite>" > test-results.xml
          fi
        '''
        junit allowEmptyResults: true, testResults: 'test-results.xml'
      }
    }

    stage('Package') {
      steps {
        sh '''
          echo ">>> Package step"
          mkdir -p dist
          echo "build artifact $(date)" > dist/artifact.txt
        '''
        archiveArtifacts artifacts: 'dist/**', fingerprint: true
      }
    }
  }

  post {
    always {
      echo "Build finished: ${currentBuild.currentResult}"
    }
  }
}
