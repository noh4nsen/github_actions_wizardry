pipeline {
  agent any

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '30'))
  }

  parameters {
    choice(name: 'ACTION', choices: ['plan','apply','destroy'], description: 'Terraform action')
    choice(name: 'ENV',    choices: ['dev','stg','prod'],       description: 'env/<ENV>.tfvars if present')
    string(name: 'TF_DIR', defaultValue: 'terraform',           description: 'Path to Terraform project')
  }

  environment {
    TF_IN_AUTOMATION = 'true'
    TF_INPUT         = '0'
    TF_VERSION       = '1.7.5'
    PATH             = "${env.WORKSPACE}/bin:${env.PATH}"
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Install Terraform') {
      steps {
        sh '''
          set -euo pipefail
          mkdir -p "$WORKSPACE/bin"
          if ! command -v terraform >/dev/null 2>&1; then
            OS=linux; ARCH=amd64
            URL="https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_${OS}_${ARCH}.zip"
            echo "Downloading $URL"
            if command -v curl >/dev/null 2>&1; then
              curl -fsSLo tf.zip "$URL"
            else
              wget -qO tf.zip "$URL"
            fi
            # Use the JDK 'jar' tool to unzip (works even if 'unzip' isn't installed)
            (cd "$WORKSPACE/bin" && jar xf ../tf.zip)
            rm -f tf.zip
            chmod +x "$WORKSPACE/bin/terraform"
          fi
          terraform -version
        '''
      }
    }

    stage('Fmt & Validate') {
      steps {
        dir("${params.TF_DIR}") {
          sh '''
            set -euo pipefail
            terraform fmt -check -recursive
            terraform init -input=false -no-color
            terraform validate -no-color
          '''
        }
      }
    }

    stage('Plan') {
      when {
        anyOf { expression { params.ACTION == 'plan' }; expression { params.ACTION == 'apply' } }
      }
      steps {
        dir("${params.TF_DIR}") {
          sh '''
            set -euo pipefail
            EXTRA=""
            [ -f "env/${ENV}.tfvars" ] && EXTRA="-var-file=env/${ENV}.tfvars"
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
          sh 'set -euo pipefail; terraform apply -input=false -auto-approve tfplan'
        }
      }
    }

    stage('Destroy (manual gate)') {
      when { expression { params.ACTION == 'destroy' } }
      steps {
        input message: "Destroy ALL resources in ${params.ENV}? This is irreversible.", ok: "Destroy"
        dir("${params.TF_DIR}") {
          sh '''
            set -euo pipefail
            EXTRA=""
            [ -f "env/${ENV}.tfvars" ] && EXTRA="-var-file=env/${ENV}.tfvars"
            terraform destroy -input=false -auto-approve -no-color $EXTRA
          '''
        }
      }
    }
  }

  post {
    always {
      dir("${params.TF_DIR}") {
        archiveArtifacts artifacts: ".terraform/**,.terraform.lock.hcl,terraform.tfstate*", allowEmptyArchive: true
      }
    }
  }
}
