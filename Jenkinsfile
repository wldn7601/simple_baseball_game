pipeline {
    agent any

    environment {
        IMAGE = "wldn7601/baseball_game"
        COMPOSE = "/usr/bin/docker compose"
        PROJECT_DIR = "/workspace/baseball_game"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set Tags') {
            steps {
                script {
                    env.SHORT_SHA = sh(script: "git rev-parse --short=7 HEAD", returnStdout: true).trim()
                    env.DATE_TAG  = sh(script: "date +%Y%m%d", returnStdout: true).trim()
                    env.BUILD_TAG = "jenkins-${env.DATE_TAG}-${env.SHORT_SHA}"
                }
                echo "BUILD TAG: ${env.BUILD_TAG}"
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub',
                                                 usernameVariable: 'DH_USER',
                                                 passwordVariable: 'DH_PASS')]) {
                    sh 'echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin'
                }
            }
        }

        stage('Build & Push') {
            steps {
                sh """
                    docker build -t ${IMAGE}:${BUILD_TAG} -t ${IMAGE}:latest .
                    docker push ${IMAGE}:${BUILD_TAG}
                    docker push ${IMAGE}:latest
                """
            }
        }

        stage('Deploy to Kakao Cloud') {
          steps {
            sshagent(['kakaocloud-key-pjw']) {
                sh '''
                    ssh -o StrictHostKeyChecking=no ubuntu@host-10-0-0-179 "
                        cd /home/ubuntu/baseball_game &&
                        docker compose pull &&
                        docker compose down &&
                        docker compose up -d
                    "
                '''
                }
            }
        }

        stage('Cleanup') {
            steps {
                sh "docker image prune -f || true"
            }
        }
    }
}
