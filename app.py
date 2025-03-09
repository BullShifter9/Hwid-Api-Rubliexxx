# app.py - HWID Storage System for Render.com
from flask import Flask, request, jsonify
import os
import json
import time
from datetime import datetime
import hashlib
from functools import wraps

app = Flask(__name__)

# Configuration
DATABASE_FILE = "hwid_database.json"
API_KEY = os.environ.get("API_KEY", "Supernaturalshithappenonearthniggers90908080")  # Set this in Render environment variables

# Database functions
def load_database():
    """Load the HWID database from file or create if it doesn't exist."""
    try:
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, "r") as file:
                return json.load(file)
        else:
            # Create default database structure
            default_db = {
                "hwids": [],
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
            save_database(default_db)
            return default_db
    except Exception as e:
        print(f"Error loading database: {e}")
        return {"hwids": [], "metadata": {"error": str(e)}}

def save_database(data):
    """Save the database to file."""
    try:
        with open(DATABASE_FILE, "w") as file:
            json.dump(data, file, indent=2)
        return True
    except Exception as e:
        print(f"Error saving database: {e}")
        return False

# Authentication decorator
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing API key"}), 401
            
        token = auth_header.split(" ")[1]
        if token != API_KEY:
            return jsonify({"error": "Invalid API key"}), 401
            
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route("/api/hwid", methods=["POST"])
@require_api_key
def store_hwid():
    """Store HWID data received from Roblox client."""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get("hwid"):
            return jsonify({"error": "Missing HWID in request"}), 400
            
        # Load database
        database = load_database()
        
        # Current timestamp
        current_time = datetime.now().isoformat()
        
        # Check if HWID already exists
        existing_hwid = next((item for item in database["hwids"] if item["hwid"] == data["hwid"]), None)
        
        if existing_hwid:
            # Update existing entry
            existing_hwid.update({
                "player": data.get("player", existing_hwid.get("player", {})),
                "game": data.get("game", existing_hwid.get("game", {})),
                "system": data.get("system", existing_hwid.get("system", {})),
                "executor": data.get("executor", existing_hwid.get("executor")),
                "last_seen": current_time,
                "access_count": existing_hwid.get("access_count", 0) + 1
            })
            
            # Add this player to players list if not already there
            if "players" not in existing_hwid:
                existing_hwid["players"] = []
                
            if data.get("player") and data["player"].get("userId"):
                player_id = str(data["player"]["userId"])
                player_exists = any(p.get("userId") == player_id for p in existing_hwid["players"])
                
                if not player_exists:
                    existing_hwid["players"].append({
                        "userId": player_id,
                        "username": data["player"].get("username", "Unknown"),
                        "first_seen": current_time
                    })
        else:
            # Create new entry
            new_entry = {
                "hwid": data["hwid"],
                "executor": data.get("executor", "Unknown"),
                "player": data.get("player", {}),
                "game": data.get("game", {}),
                "system": data.get("system", {}),
                "created_at": current_time,
                "last_seen": current_time,
                "access_count": 1,
                "allowed": False,  # Default to not allowed
                "players": []
            }
            
            # Add initial player if provided
            if data.get("player") and data["player"].get("userId"):
                new_entry["players"].append({
                    "userId": str(data["player"]["userId"]),
                    "username": data["player"].get("username", "Unknown"),
                    "first_seen": current_time
                })
                
            database["hwids"].append(new_entry)
        
        # Save the updated database
        if save_database(database):
            return jsonify({
                "success": True,
                "message": "HWID data stored successfully",
                "timestamp": current_time,
                "total_entries": len(database["hwids"])
            })
        else:
            return jsonify({"error": "Failed to save database"}), 500
            
    except Exception as e:
        print(f"Error processing HWID: {e}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/hwid/check/<hwid>", methods=["GET"])
@require_api_key
def check_hwid(hwid):
    """Check if a HWID exists and is allowed."""
    try:
        database = load_database()
        
        # Find the HWID entry
        hwid_entry = next((item for item in database["hwids"] if item["hwid"] == hwid), None)
        
        if hwid_entry:
            # Update last checked time
            hwid_entry["last_checked"] = datetime.now().isoformat()
            save_database(database)
            
            return jsonify({
                "exists": True,
                "allowed": hwid_entry.get("allowed", False),
                "first_seen": hwid_entry.get("created_at"),
                "executor": hwid_entry.get("executor", "Unknown")
            })
        else:
            return jsonify({
                "exists": False,
                "allowed": False
            })
            
    except Exception as e:
        print(f"Error checking HWID: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/hwid", methods=["GET"])
@require_api_key
def get_all_hwids():
    """Get all HWIDs (admin endpoint)."""
    try:
        database = load_database()
        return jsonify(database)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/hwid/allow/<hwid>", methods=["POST"])
@require_api_key
def allow_hwid(hwid):
    """Set a HWID as allowed."""
    try:
        database = load_database()
        
        # Find the HWID entry
        hwid_entry = next((item for item in database["hwids"] if item["hwid"] == hwid), None)
        
        if hwid_entry:
            hwid_entry["allowed"] = True
            hwid_entry["allowed_at"] = datetime.now().isoformat()
            
            if save_database(database):
                return jsonify({
                    "success": True,
                    "message": f"HWID {hwid} is now allowed"
                })
            else:
                return jsonify({"error": "Failed to save changes"}), 500
        else:
            return jsonify({"error": "HWID not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/hwid/disallow/<hwid>", methods=["POST"])
@require_api_key
def disallow_hwid(hwid):
    """Remove a HWID from allowed list."""
    try:
        database = load_database()
        
        # Find the HWID entry
        hwid_entry = next((item for item in database["hwids"] if item["hwid"] == hwid), None)
        
        if hwid_entry:
            hwid_entry["allowed"] = False
            hwid_entry["disallowed_at"] = datetime.now().isoformat()
            
            if save_database(database):
                return jsonify({
                    "success": True,
                    "message": f"HWID {hwid} is now disallowed"
                })
            else:
                return jsonify({"error": "Failed to save changes"}), 500
        else:
            return jsonify({"error": "HWID not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stats", methods=["GET"])
@require_api_key
def get_stats():
    """Get system statistics."""
    try:
        database = load_database()
        
        # Calculate statistics
        total_hwids = len(database["hwids"])
        allowed_hwids = sum(1 for item in database["hwids"] if item.get("allowed", False))
        
        # Count unique executors
        executors = {}
        for item in database["hwids"]:
            executor = item.get("executor", "Unknown")
            executors[executor] = executors.get(executor, 0) + 1
        
        # Get recently seen HWIDs
        now = datetime.now()
        recently_active = []
        
        for item in database["hwids"]:
            if "last_seen" in item:
                try:
                    last_seen = datetime.fromisoformat(item["last_seen"])
                    time_diff = (now - last_seen).total_seconds() / 3600  # Hours
                    
                    if time_diff < 24:  # Active in last 24 hours
                        recently_active.append({
                            "hwid": item["hwid"],
                            "executor": item.get("executor", "Unknown"),
                            "username": item.get("player", {}).get("username", "Unknown"),
                            "hours_ago": round(time_diff, 1)
                        })
                except:
                    pass
        
        return jsonify({
            "total_hwids": total_hwids,
            "allowed_hwids": allowed_hwids,
            "executor_breakdown": executors,
            "recently_active": recently_active,
            "system_time": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
