from flask import Flask, request, jsonify
import os
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Environment variables
REPLIT_URL = os.environ.get("REPLIT_URL", "https://ccf11408-beea-454f-845b-1594c0f427af-00-3eu3dcqn0pks2.pike.replit.dev/")
ADMIN_KEY = os.environ.get("ADMIN_KEY", "Supernaturalshithappenonearthniggers90908080")

@app.route("/verify", methods=["POST"])
def verify_hwid():
    try:
        data = request.get_json()
        
        if not data or "hwid" not in data:
            return jsonify({"success": False, "message": "Invalid request"}), 400
            
        hwid = data["hwid"]
        
        # Fetch HWID list from Replit
        response = requests.get(f"{REPLIT_URL}/hwids")
        
        if response.status_code != 200:
            return jsonify({"success": False, "message": "Database error"}), 500
            
        hwids_data = response.json()
        
        is_authorized = hwid in hwids_data.get("hwids", [])
        is_admin = hwid in hwids_data.get("admin_hwids", [])
        
        return jsonify({
            "success": is_authorized,
            "admin": is_admin,
            "message": "Authorized" if is_authorized else "Unauthorized"
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

@app.route("/admin", methods=["POST"])
def admin_panel():
    data = request.get_json()
    
    if not data or "admin_key" not in data:
        return jsonify({"success": False, "message": "Invalid request"}), 400
        
    if data["admin_key"] != ADMIN_KEY:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    # Forward to Replit
    response = requests.post(f"{REPLIT_URL}/manage", json=data)
    
    if response.status_code != 200:
        return jsonify({"success": False, "message": "Database operation failed"}), 500
        
    return response.json()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
