#!/bin/bash
# Authenticate and Tag Docker Image for Amazon ECR

# Set your AWS region and account ID
AWS_REGION=us-east-1
AWS_ACCOUNT_ID="your-id"

# Authenticate Docker to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Tag the Docker image
docker tag langchain-econ-flask-app:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/langchain-econ-repo:latest
