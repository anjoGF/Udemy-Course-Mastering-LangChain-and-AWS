#!/bin/bash
# Run Docker container

docker run --name langchain-app --network langchain-network -d -p 5000:5000 \
  -v $(pwd)/project:/app/database \
  -e OPENAI_API_KEY="<your-api-key>" \
  -e SERPAPI_API_KEY="<your-api-key>" \
  -e DATABASE_URI=sqlite:////app/database/financial_data.db \
  -e REDIS_URL=redis://langchain-redis:6379/0 \
  langchain-econ-flask-app



