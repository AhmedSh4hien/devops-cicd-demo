pipeline {
    agent any

        triggers {
        pollSCM('H/2 * * * *')
    }

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

                stage('Deploy') {
            steps {
                withCredentials([string(credentialsId: 'ec2-host', variable: 'EC2_HOST')]) {
                    sshagent(credentials: ['ec2-ssh-key']) {
                        sh '''
                            ssh -o StrictHostKeyChecking=accept-new ec2-user@$EC2_HOST "mkdir -p ~/app"
                            scp -o StrictHostKeyChecking=accept-new deploy/compose.yaml ec2-user@$EC2_HOST:~/app/compose.yaml
                            ssh ec2-user@$EC2_HOST "cd ~/app && IMAGE_TAG=$IMAGE_TAG docker compose pull && IMAGE_TAG=$IMAGE_TAG docker compose up -d"
                        '''
                    }
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