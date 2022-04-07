pipeline {
    agent { label 'small' }
    environment {
      imagename = "ghcr.io/pilotdataplatform/metadata"
      commit = sh(returnStdout: true, script: 'git describe --always').trim()
      registryCredential = 'pilot-ghcr'
      dockerImage = ''
    }

    stages {

    stage('DEV Git clone') {
        when { branch 'k8s-dev' }
        steps {
            git branch: 'k8s-dev',
                url: 'https://git.indocresearch.org/pilot/metadata.git',
                credentialsId: 'lzhao'
        }
    }

    stage('DEV Run unit tests') {
        when { branch 'k8s-dev' }
        steps {
            withCredentials([
                usernamePassword(credentialsId: 'indoc-ssh', usernameVariable: 'SUDO_USERNAME', passwordVariable: 'SUDO_PASSWORD'),
                string(credentialsId:'VAULT_TOKEN', variable: 'VAULT_TOKEN'),
                string(credentialsId:'VAULT_URL', variable: 'VAULT_URL'),
                file(credentialsId:'VAULT_CRT', variable: 'VAULT_CRT')
            ]) {
                sh """
                export OPSDB_UTILILT_USERNAME=postgres
                export OPSDB_UTILILT_PASSWORD=postgres
                export OPSDB_UTILILT_HOST=db
                export OPSDB_UTILILT_PORT=5432
                export OPSDB_UTILILT_NAME=metadata
                [ ! -f /data/docker2/jenkins/workspace/VRE_metadata_k8s-dev/.env ] && touch /data/docker2/jenkins/workspace/VRE_metadata_k8s-dev/.env
                [ -d /data/docker2/jenkins/workspace/VRE_metadata_k8s-dev/local_config/pgadmin/sessions ] && sudo chmod 777 -R -f /data/docker2/jenkins/workspace/VRE_metadata_k8s-dev/local_config/pgadmin/sessions
                sudo chmod 777 -R -f /data/docker2/jenkins/workspace/VRE_metadata_k8s-dev/local_config/pgadmin/sessions                
                docker build -t web .
                docker-compose -f docker-compose.yaml down -v
                docker-compose up -d
                sleep 10s
                docker-compose exec -T web /bin/bash
                pwd
                hostname
                docker-compose exec -T web pip install --user poetry==1.1.12
                docker-compose exec -T web poetry config virtualenvs.in-project false
                docker-compose exec -T web poetry install --no-root --no-interaction
                docker-compose exec -T web poetry run pytest --verbose -c tests/pytest.ini
                docker-compose -f docker-compose.yaml down -v
                """
            }
        }
    }

    stage('DEV Build and push image') {
      when {branch "k8s-dev"}
      steps {
        script {
          docker.withRegistry('ghcr.io', registryCredential) {
              customImage = docker.build("$imagename:$commit")
              customImage.push()
          }
        }
      }
    }

    stage('DEV Remove image') {
      when {branch "k8s-dev"}
      steps{
        sh "docker rmi $imagename:$commit"
      }
    }

    stage('DEV Deploy') {
      when {branch "k8s-dev"}
      steps{
        build(job: "/VRE-IaC/UpdateAppVersion", parameters: [
          [$class: 'StringParameterValue', name: 'TF_TARGET_ENV', value: 'dev' ],
          [$class: 'StringParameterValue', name: 'TARGET_RELEASE', value: 'metadata' ],
          [$class: 'StringParameterValue', name: 'NEW_APP_VERSION', value: "$commit" ]
        ])
      }
    }

    stage('STAGING Git clone') {
        when { branch 'k8s-staging' }
        steps {
            git branch: 'k8s-staging',
                url: 'https://git.indocresearch.org/pilot/metadata.git',
                credentialsId: 'lzhao'
        }
    }

    stage('STAGING Build and push image') {
      when {branch "k8s-staging"}
      steps {
        script {
          docker.withRegistry('ghcr.io', registryCredential) {
              customImage = docker.build("$imagename:$commit")
              customImage.push()
          }
        }
      }
    }

    stage('STAGING Remove image') {
      when {branch "k8s-staging"}
      steps{
        sh "docker rmi $imagename:$commit"
      }
    }

    stage('STAGING Deploy') {
      when {branch "k8s-staging"}
      steps{
        build(job: "/VRE-IaC/Staging-UpdateAppVersion", parameters: [
          [$class: 'StringParameterValue', name: 'TF_TARGET_ENV', value: 'staging' ],
          [$class: 'StringParameterValue', name: 'TARGET_RELEASE', value: 'metadata' ],
          [$class: 'StringParameterValue', name: 'NEW_APP_VERSION', value: "$commit" ]
        ])
      }
    }
  }
  post {
      failure {
        slackSend color: '#FF0000', message: "Build Failed! - ${env.JOB_NAME} $commit  (<${env.BUILD_URL}|Open>)", channel: 'jenkins-dev-staging-monitor'
      }
  }

}
