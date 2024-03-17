#!/bin/bash
# Set your AWS region and account ID
AWS_REGION=us-east-1
AWS_ACCOUNT_ID="your-id"

# Push the image
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/langchain-econ-repo:latest
