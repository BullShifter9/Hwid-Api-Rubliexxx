from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Path to the HWID database file
HWID_DB_PATH = "hwid_database.json"

# Initialize database file if it doesn't exist
if not os.path.exists(HWID_DB_PATH):
    with open(HWID_DB_PATH, "w") as f:
        json.dump({"authorized": []}, f)

# Load HWID database
def load_hwid_database():
    try:
        with open(HWID_DB_PATH, "r") as f:
            return json.load(f)
    except:
        # Return empty database if file is corrupted or empty
        return {"authorized": []}

# Save HWID database
def save_hwid_database(data):
    with open(HWID_DB_PATH, "w") as f:
        json.dump(data, f)

# API endpoint to verify HWID
@app.route('/verify', methods=['POST'])
def verify_hwid():
    data = request.json
    
    # Validate request data
    if not data or 'hwid' not in data:
        return jsonify({"success": False, "message": "Invalid request"}), 400
    
    hwid = data['hwid']
    hwid_db = load_hwid_database()
    
    # Check if HWID is authorized
    if hwid in hwid_db["authorized"]:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Unauthorized HWID"}), 401

# API endpoint to add HWID
@app.route('/manage', methods=['POST'])
def manage_hwid():
    data = request.json
    
    # Validate request data and admin key
    if not data or 'action' not in data or 'hwid' not in data or 'admin_key' not in data:
        return jsonify({"success": False, "message": "Invalid request"}), 400
    
    # Simple admin key validation
    admin_key = os.environ.get('ADMIN_KEY', 'Supernaturalshithappenonearthniggers90908080')
    if data['admin_key'] != admin_key:
        return jsonify({"success": False, "message": "Unauthorized access"}), 401
    
    hwid = data['hwid']
    action = data['action']
    hwid_db = load_hwid_database()
    
    # Process the requested action
    if action == "add":
        if hwid not in hwid_db["authorized"]:
            hwid_db["authorized"].append(hwid)
        
        save_hwid_database(hwid_db)
        return jsonify({"success": True, "message": "HWID added successfully"})
    
    elif action == "remove":
        if hwid in hwid_db["authorized"]:
            hwid_db["authorized"].remove(hwid)
        
        save_hwid_database(hwid_db)
        return jsonify({"success": True, "message": "HWID removed successfully"})
    
    else:
        return jsonify({"success": False, "message": "Invalid action"}), 400

# API endpoint to list all HWIDs
@app.route('/list', methods=['POST'])
def list_hwids():
    data = request.json
    
    # Validate admin key
    if not data or 'admin_key' not in data:
        return jsonify({"success": False, "message": "Invalid request"}), 400
    
    admin_key = os.environ.get('ADMIN_KEY', 'Supernaturalshithappenonearthniggers90908080')
    if data['admin_key'] != admin_key:
        return jsonify({"success": False, "message": "Unauthorized access"}), 401
    
    hwid_db = load_hwid_database()
    return jsonify({
        "success": True,
        "hwids": hwid_db["authorized"]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
