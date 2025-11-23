from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
import os
import certifi
import ssl

# Import database setup functions
from setup_database import init_database_if_empty, get_mongo_client

app = Flask(__name__)
CORS(app)

# MongoDB connection with proper SSL configuration
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')

# Configure MongoDB client with SSL settings for Render compatibility
try:
    print(f"🔗 Attempting MongoDB connection...")
    
    # Parse the URI to check if it's using mongodb+srv
    is_srv = MONGO_URI.startswith('mongodb+srv://')
    
    if is_srv:
        # For mongodb+srv:// connections - minimal config
        client = MongoClient(
            MONGO_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=30000
        )
    else:
        # For standard mongodb:// connections
        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=30000
        )
    
    # Test the connection
    client.admin.command('ping')
    print("✅ MongoDB connected successfully!")
except Exception as e:
    print(f"⚠️ MongoDB connection error: {e}")
    print("⚠️ App will run but database operations will fail")
    client = None
db = client['flask_db'] if client is not None else None
tasks_collection = db['tasks'] if db is not None else None
users_collection = db['users'] if db is not None else None

# Initialize database with sample data if empty (runs once on startup)
if client is not None and db is not None:
    try:
        init_database_if_empty(db)
    except Exception as e:
        print(f"⚠️  Could not initialize database: {e}")
else:
    print("⚠️ MongoDB client not initialized")

# Helper function to convert ObjectId to string
def serialize_task(task):
    if task:
        task['_id'] = str(task['_id'])
        return task
    return None

# Root endpoint - serve the HTML interface
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# API documentation endpoint
@app.route('/api')
def api_docs():
    return jsonify({
        "message": "Welcome to the Simple API with MongoDB",
        "database": "MongoDB Atlas",
        "endpoints": {
            "GET /": "Web interface",
            "GET /api": "This help message",
            "GET /api/tasks": "Get all tasks",
            "GET /api/tasks/<id>": "Get a specific task",
            "POST /api/tasks": "Create a new task",
            "PUT /api/tasks/<id>": "Update a task",
            "DELETE /api/tasks/<id>": "Delete a task",
            "GET /api/time": "Get current server time",
            "GET /api/health": "Health check",
            "POST /api/setup": "Reset database with sample data"
        }
    })

# Get all tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = list(tasks_collection.find())
    for task in tasks:
        task['_id'] = str(task['_id'])
    return jsonify({"tasks": tasks, "count": len(tasks)})

# Get a specific task
@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    try:
        task = tasks_collection.find_one({"_id": ObjectId(task_id)})
        if task:
            return jsonify(serialize_task(task))
        return jsonify({"error": "Task not found"}), 404
    except:
        return jsonify({"error": "Invalid task ID"}), 400

# Create a new task
@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    new_task = {
        "title": data["title"],
        "completed": data.get("completed", False),
        "priority": data.get("priority", "medium"),
        "description": data.get("description", ""),
        "created_at": datetime.now().isoformat()
    }
    
    result = tasks_collection.insert_one(new_task)
    new_task['_id'] = str(result.inserted_id)
    
    return jsonify(new_task), 201

# Update a task
@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        data = request.get_json()
        update_data = {}
        
        if 'title' in data:
            update_data['title'] = data['title']
        if 'completed' in data:
            update_data['completed'] = data['completed']
        if 'priority' in data:
            update_data['priority'] = data['priority']
        if 'description' in data:
            update_data['description'] = data['description']
        
        update_data['updated_at'] = datetime.now().isoformat()
        
        result = tasks_collection.find_one_and_update(
            {"_id": ObjectId(task_id)},
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            return jsonify(serialize_task(result))
        return jsonify({"error": "Task not found"}), 404
    except:
        return jsonify({"error": "Invalid task ID"}), 400

# Delete a task
@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        result = tasks_collection.delete_one({"_id": ObjectId(task_id)})
        if result.deleted_count:
            return jsonify({"message": "Task deleted successfully"})
        return jsonify({"error": "Task not found"}), 404
    except:
        return jsonify({"error": "Invalid task ID"}), 400

# Get current time
@app.route('/api/time', methods=['GET'])
def get_time():
    return jsonify({
        "current_time": datetime.now().isoformat(),
        "timezone": "UTC",
        "database": "MongoDB Connected" if client.server_info() else "MongoDB Disconnected"
    })

# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        client.server_info()
        task_count = tasks_collection.count_documents({})
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "tasks_count": task_count,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# Reset database with sample data (manual trigger)
@app.route('/api/setup', methods=['POST'])
def reset_database():
    """
    Endpoint to manually reset database with sample data
    Useful for testing or resetting to initial state
    """
    try:
        from setup_database import setup_database
        
        # This will clear and repopulate the database
        print("\n🔄 Manual database reset triggered via API...")
        
        # Clear existing data
        tasks_collection.delete_many({})
        users_collection.delete_many({})
        
        # Re-initialize
        init_database_if_empty(db)
        
        task_count = tasks_collection.count_documents({})
        user_count = users_collection.count_documents({})
        
        return jsonify({
            "message": "Database reset successfully",
            "tasks_created": task_count,
            "users_created": user_count
        }), 200
    except Exception as e:
        return jsonify({
            "error": "Failed to reset database",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Starting Flask server with MongoDB")
    print("="*50)
    print(f"📊 Database: flask_db")
    print(f"🔗 MongoDB: {MONGO_URI[:30]}...")
    print(f"🌐 Server: http://localhost:5001")
    print(f"📋 API Docs: http://localhost:5001/api")
    print(f"💚 Health Check: http://localhost:5001/api/health")
    print("="*50)
    print("\nPress CTRL+C to stop the server\n")
    app.run(debug=True, host='0.0.0.0', port=5001)