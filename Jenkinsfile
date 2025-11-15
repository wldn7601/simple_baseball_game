pipeline {
    agent any

    environment {
        IMAGE_NAME = "wldn7601/baseball_game"
        PROJECT_DIR = "/home/ubuntu/baseball_game"
        DOCKER_COMPOSE = "/usr/bin/docker compose"  // jenkins 컨테이너에 설치된 compose 플러그인 경로
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh """
                    docker build -t ${IMAGE_NAME}:latest .
                """
            }
        }

        stage('Login to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub', 
                                                 usernameVariable: 'DOCKERHUB_USER', 
                                                 passwordVariable: 'DOCKERHUB_PASS')]) {
                    sh """
                        echo "${DOCKERHUB_PASS}" | docker login -u "${DOCKERHUB_USER}" --password-stdin
                    """
                }
            }
        }

        stage('Push to DockerHub') {
            steps {
                sh """
                    docker push ${IMAGE_NAME}:latest
                """
            }
        }

        stage('Deploy to Server') {
            steps {
                sh """
                    cd ${PROJECT_DIR}

                    # docker-compose 파일 업데이트해도 됨
                    docker pull ${IMAGE_NAME}:latest

                    ${DOCKER_COMPOSE} down
                    ${DOCKER_COMPOSE} up -d
                """
            }
        }

        stage('Health Check') {
            steps {
                script {
                    def status = sh(
                        script: "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5001",
                        returnStdout: true
                    ).trim()

                    if (status != '200') {
                        error "Health check failed! Code=${status}"
                    }
                }
            }
        }
    }

    post {
        success {
            echo "배포 성공!"
        }
        failure {
            echo "배포 실패. 로그를 확인하십시오."
        }
    }
}
