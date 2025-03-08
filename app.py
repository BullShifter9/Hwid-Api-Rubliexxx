from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Storage for captured HWIDs
HWID_DATABASE = "hwid_database.json"

def load_database():
    if os.path.exists(HWID_DATABASE):
        try:
            with open(HWID_DATABASE, "r") as file:
                return json.load(file)
        except:
            return {"hwids": []}
    else:
        return {"hwids": []}

def save_database(data):
    with open(HWID_DATABASE, "w") as file:
        json.dump(data, file, indent=2)

@app.route('/api/hwid', methods=['POST'])
def capture_hwid():
    # Verify API key for security
    api_key = request.headers.get('Authorization')
    if api_key != os.environ.get('f8a03e7fb6e29c4ba59f838e85b932b7'):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    # Process data
    data = request.json
    database = load_database()
    
    # Add timestamp and unique identifier
    data["timestamp"] = datetime.now().isoformat()
    data["id"] = len(database["hwids"]) + 1
    
    # Store HWID data
    database["hwids"].append(data)
    save_database(database)
    
    return jsonify({"status": "success", "message": "HWID captured"}), 200

@app.route('/api/hwids', methods=['GET'])
def get_all_hwids():
    # Verify API key
    api_key = request.headers.get('Authorization')
    if api_key != os.environ.get('API_SECRET_KEY'):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    database = load_database()
    return jsonify(database), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
