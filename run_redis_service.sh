#!/bin/bash
# Authenticate and Tag Docker Image for Amazon ECR

docker run --name langchain-redis --network langchain-network -d -p 6379:6379 redis redis-server --save 60 1 --loglevel warning