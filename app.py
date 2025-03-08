from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/api/hwid', methods=['POST'])
def capture_hwid():
    api_key = request.headers.get('Authorization')
    if api_key != os.environ.get('API_SECRET_KEY'):
        return jsonify({"status": "error"}), 401
    
    return jsonify({"status": "success"}), 200

@app.route('/api/hwids', methods=['GET'])
def get_all_hwids():
    api_key = request.headers.get('Authorization')
    if api_key != os.environ.get('API_SECRET_KEY'):
        return jsonify({"status": "error"}), 401
    
    return jsonify({"hwids":[]}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
