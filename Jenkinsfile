pipeline {
    agent any

    parameters {
        choice(
            name: 'ACTION',
            choices: ['build-only', 'deploy', 'destroy'],
            description: 'build-only: build and push image. deploy: also provision EC2 with Terraform and deploy. destroy: tear down EC2.'
        )
    }

    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        IMAGE_REPO = 'shahien4/devops-cicd-demo'
        IMAGE_TAG  = "1.0.${env.BUILD_NUMBER}"
    }

    stages {
        stage('Build image') {
            when { expression { params.ACTION != 'destroy' } }
            steps {
                sh 'docker build --build-arg APP_VERSION=$IMAGE_TAG -t $IMAGE_REPO:$IMAGE_TAG -t $IMAGE_REPO:latest .'
            }
        }

        stage('Push image') {
            when { expression { params.ACTION != 'destroy' } }
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

        stage('Provision (Terraform)') {
            when { expression { params.ACTION in ['deploy', 'destroy'] } }
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY'),
                    file(credentialsId: 'ec2-public-key', variable: 'PUBKEY_FILE')
                ]) {
                    dir('terraform/ec2') {
                        sh '''
                            MY_IP=$(curl -s https://checkip.amazonaws.com | tr -d '[:space:]')
                            terraform init -input=false
                            if [ "$ACTION" = "destroy" ]; then
                                terraform destroy -auto-approve -input=false \
                                    -var="my_ip_cidr=$MY_IP/32" -var="public_key_path=$PUBKEY_FILE"
                            else
                                terraform apply -auto-approve -input=false \
                                    -var="my_ip_cidr=$MY_IP/32" -var="public_key_path=$PUBKEY_FILE"
                                terraform output -raw instance_public_ip > "$WORKSPACE/ec2_ip.txt"
                            fi
                        '''
                    }
                }
            }
        }

        stage('Deploy') {
            when { expression { params.ACTION == 'deploy' } }
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {
                    sh '''
                        EC2_HOST=$(cat ec2_ip.txt)
                        SSH_OPTS="-o StrictHostKeyChecking=accept-new -o ConnectTimeout=10"

                        for i in $(seq 1 30); do
                            ssh $SSH_OPTS ec2-user@$EC2_HOST "cloud-init status --wait" && break
                            echo "Waiting for server ($i/30)..."
                            sleep 10
                        done

                        ssh $SSH_OPTS ec2-user@$EC2_HOST "mkdir -p ~/app"
                        scp $SSH_OPTS deploy/compose.yaml ec2-user@$EC2_HOST:~/app/compose.yaml
                        ssh $SSH_OPTS ec2-user@$EC2_HOST "cd ~/app && IMAGE_TAG=$IMAGE_TAG docker compose pull && IMAGE_TAG=$IMAGE_TAG docker compose up -d"
                        echo "App is live at http://$EC2_HOST:8080"
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