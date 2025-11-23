from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory data storage
tasks = [
    {"id": 1, "title": "Learn Python", "completed": False},
    {"id": 2, "title": "Build an API", "completed": True}
]

# Root endpoint
@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Simple API",
        "endpoints": {
            "GET /": "This help message",
            "GET /api/tasks": "Get all tasks",
            "GET /api/tasks/<id>": "Get a specific task",
            "POST /api/tasks": "Create a new task",
            "PUT /api/tasks/<id>": "Update a task",
            "DELETE /api/tasks/<id>": "Delete a task",
            "GET /api/time": "Get current server time"
        }
    })

# Get all tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify({"tasks": tasks, "count": len(tasks)})

# Get a specific task
@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task:
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

# Create a new task
@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    new_task = {
        "id": max([t["id"] for t in tasks], default=0) + 1,
        "title": data["title"],
        "completed": data.get("completed", False)
    }
    tasks.append(new_task)
    return jsonify(new_task), 201

# Update a task
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    data = request.get_json()
    task["title"] = data.get("title", task["title"])
    task["completed"] = data.get("completed", task["completed"])
    return jsonify(task)

# Delete a task
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    tasks = [t for t in tasks if t["id"] != task_id]
    return jsonify({"message": "Task deleted successfully"})

# Get current time
@app.route('/api/time', methods=['GET'])
def get_time():
    return jsonify({
        "current_time": datetime.now().isoformat(),
        "timezone": "UTC"
    })

if __name__ == '__main__':
    print("🚀 Starting Flask server on http://localhost:5001")
    print("📋 API Documentation: http://localhost:5001")
    print("⏰ Test endpoint: http://localhost:5001/api/time")
    print("📝 Tasks endpoint: http://localhost:5001/api/tasks")
    print("\nPress CTRL+C to stop the server\n")
    app.run(debug=True, host='0.0.0.0', port=5001)