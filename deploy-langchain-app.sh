#!/bin/bash
# Define your variables
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="your-id"
OPENAI_API_KEY="<your-api-key>"
SERPAPI_API_KEY="<your-serp-api-key>"
ECS_CLUSTER_NAME="langchain-cluster"
ECS_SERVICE_NAME="langchain-service"
ECS_TASK_DEFINITION="langchain-task"
ECR_REPOSITORY_NAME="langchain-econ-flask-app"
VPC_ID="vpc-id" # Replace w/your VPC ID
SUBNET_IDS="your-subnet-id,your-subnet-id" # Replace w/your Subnet IDs
SECURITY_GROUP_NAME="langchain-sg"
SECURITY_GROUP_DESC="Langchain ECS service SG"

# Ensure AWS CLI is configured
aws configure list

# Build Docker image
docker build -t $ECR_REPOSITORY_NAME .

# Create Docker Network if not exists
if [ -z "$(docker network ls --filter name=^langchain-network$ --format '{{.Name}}')" ]; then
    docker network create langchain-network
fi

# Run Redis container if not already running
if [ -z "$(docker ps -a --filter name=^langchain-redis$ --format '{{.Names}}')" ]; then
    docker run --name langchain-redis --network langchain-network -d -p 6379:6379 redis redis-server --save 60 1 --loglevel warning
fi

# Authenticate Docker to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Create ECR repository if not exists
if aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME --region $AWS_REGION 2>&1 | grep -q RepositoryNotFoundException; then
    aws ecr create-repository --repository-name $ECR_REPOSITORY_NAME --region $AWS_REGION
fi

# Tag Docker image for ECR
docker tag $ECR_REPOSITORY_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:latest

# Push the image to ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:latest

# Create ECS cluster if not exists
if aws ecs describe-clusters --clusters $ECS_CLUSTER_NAME --query 'clusters[0].status' --output text | grep -qv ACTIVE; then
    aws ecs create-cluster --cluster-name $ECS_CLUSTER_NAME
fi

# Register ECS task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create a security group and capture its ID
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --filters Name=group-name,Values=$SECURITY_GROUP_NAME Name=vpc-id,Values=$VPC_ID --query 'SecurityGroups[0].GroupId' --output text)
if [ "$SECURITY_GROUP_ID" == "None" ]; then
    SECURITY_GROUP_ID=$(aws ec2 create-security-group --group-name $SECURITY_GROUP_NAME --description "$SECURITY_GROUP_DESC" --vpc-id $VPC_ID --query 'GroupId' --output text)
    # Authorize security group ingress for HTTP and HTTPS
    aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --protocol tcp --port 80 --cidr 0.0.0.0/0
    aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --protocol tcp --port 443 --cidr 0.0.0.0/0
fi

# Create an Application Load Balancer
LOAD_BALANCER_ARN=$(aws elbv2 create-load-balancer --name my-load-balancer --subnets $SUBNET_IDS --security-groups $SECURITY_GROUP_ID --query 'LoadBalancers[0].LoadBalancerArn' --output text)

# Create a target group
TARGET_GROUP_ARN=$(aws elbv2 create-target-group --name my-targets --protocol HTTP --port 80 --vpc-id $VPC_ID --query 'TargetGroups[0].TargetGroupArn' --output text)

# Create ECS service with Load Balancer configuration
if aws ecs describe-services --cluster $ECS_CLUSTER_NAME --services $ECS_SERVICE_NAME --query 'services[0].status' --output text | grep -qv ACTIVE; then
    aws ecs create-service \
        --cluster $ECS_CLUSTER_NAME \
        --service-name $ECS_SERVICE_NAME \
        --task-definition $ECS_TASK_DEFINITION \
        --desired-count 1 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SECURITY_GROUP_ID]}" \
        --load-balancers "targetGroupArn=$TARGET_GROUP_ARN,containerName=langchain-container,containerPort=5000"
fi

echo "Deployment process initiated. Check AWS Console for service status."

