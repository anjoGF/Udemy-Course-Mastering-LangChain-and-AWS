from flask import Flask, request, jsonify
import os
from initialize_agent import EconomicDataAgent

# Load environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')
DATABASE_URI = os.getenv('DATABASE_URI') 

app = Flask(__name__)

# Initialize the EconomicDataAgent with API keys and database URI
agent = EconomicDataAgent(OPENAI_API_KEY, DATABASE_URI)

@app.route('/query', methods=['POST'])
def query_agent():
    data = request.json
    query = data.get('query')

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        query_result = agent.run_agent_query(query)
        return jsonify({"response": query_result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
