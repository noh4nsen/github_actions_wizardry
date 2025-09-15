pipeline {
  // Requires Docker on the Jenkins node (or use a Docker agent node)
  agent {
    docker {
      image 'hashicorp/terraform:1.7.5'
      // workspace is mounted automatically; /bin/sh is fine
    }
  }

  options {
    timestamps()
    ansiColor('xterm')
    buildDiscarder(logRotator(numToKeepStr: '30'))
  }

  parameters {
    choice(name: 'ACTION', choices: ['plan', 'apply', 'destroy'], description: 'What to run')
    choice(name: 'ENV', choices: ['dev', 'stg', 'prod'], description: 'Loads env/<ENV>.tfvars if present')
    string(name: 'TF_DIR', defaultValue: 'terraform', description: 'Path to the Terraform project')
  }

  environment {
    TF_IN_AUTOMATION = 'true'
    TF_INPUT = '0'
    // Expose the ENV parameter to shell easily
    ENV = "${params.ENV}"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Fmt & Validate') {
      steps {
        dir("${params.TF_DIR}") {
          sh '''
            set -eu
            terraform fmt -check -recursive
            terraform init -input=false -no-color
            terraform validate -no-color
          '''
        }
      }
    }

    stage('Plan') {
      when {
        anyOf {
          expression { params.ACTION == 'plan' }
          expression { params.ACTION == 'apply' }
        }
      }
      steps {
        dir("${params.TF_DIR}") {
          sh '''
            set -eu
            EXTRA=""
            if [ -f "env/${ENV}.tfvars" ]; then EXTRA="-var-file=env/${ENV}.tfvars"; fi
            terraform plan -input=false -no-color $EXTRA -out=tfplan
            terraform show -no-color tfplan > tfplan.txt
            terraform show -json tfplan > tfplan.json || true
          '''
        }
        archiveArtifacts artifacts: "${params.TF_DIR}/tfplan,${params.TF_DIR}/tfplan.txt,${params.TF_DIR}/tfplan.json", fingerprint: true
      }
    }

    stage('Apply (manual gate)') {
      when { expression { params.ACTION == 'apply' } }
      steps {
        input message: "Apply plan to ${params.ENV}?", ok: "Apply"
        dir("${params.TF_DIR}") {
          sh 'set -eu; terraform apply -input=false -auto-approve tfplan'
        }
      }
    }

    stage('Destroy (manual gate)') {
      when { expression { params.ACTION == 'destroy' } }
      steps {
        input message: "Destroy ALL resources in ${params.ENV}? This is irreversible.", ok: "Destroy"
        dir("${params.TF_DIR}") {
          sh '''
            set -eu
            EXTRA=""
            if [ -f "env/${ENV}.tfvars" ]; then EXTRA="-var-file=env/${ENV}.tfvars"; fi
            terraform destroy -input=false -auto-approve -no-color $EXTRA
          '''
        }
      }
    }
  }

  post {
    success {
      echo "Done: ${params.ACTION} on ${params.TF_DIR} (${params.ENV})"
    }
    always {
      // Keep state + lock file (if local backend) for troubleshooting
      dir("${params.TF_DIR}") {
        archiveArtifacts artifacts: ".terraform/**,.terraform.lock.hcl,terraform.tfstate*", allowEmptyArchive: true
      }
    }
  }
}
