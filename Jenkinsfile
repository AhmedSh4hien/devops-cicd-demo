pipeline {
    agent any

    environment {
        IMAGE_REPO = 'shahien4/devops-cicd-demo'
        IMAGE_TAG  = "1.0.${env.BUILD_NUMBER}"
    }

    stages {
        stage('Build image') {
            steps {
                sh 'docker build --build-arg APP_VERSION=$IMAGE_TAG -t $IMAGE_REPO:$IMAGE_TAG -t $IMAGE_REPO:latest .'
            }
        }

        stage('Push image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DH_USER',
                    passwordVariable: 'DH_TOKEN')]) {
                    sh '''
                        echo "$DH_TOKEN" | docker login -u "$DH_USER" --password-stdin
                        docker push $IMAGE_REPO:$IMAGE_TAG
                        docker push $IMAGE_REPO:latest
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker logout || true'
        }
    }
}