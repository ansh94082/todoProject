import uuid
import logging
from datetime import datetime
from flask import request, jsonify, render_template
from app import app

# In-memory storage for tasks
tasks = []

# Priority levels
PRIORITY_LEVELS = {
    "low": {"value": 1, "color": "#27ae60"},
    "medium": {"value": 2, "color": "#f39c12"},
    "high": {"value": 3, "color": "#e74c3c"}
}

def get_task_by_id(task_id):
    """Get a task by its ID"""
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None

@app.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    try:
        # Sort tasks: incomplete first, then by priority (high to low), then by creation date
        sorted_tasks = sorted(
            tasks,
            key=lambda x: (
                x["completed"],
                -PRIORITY_LEVELS[x["priority"]]["value"],
                x["created_at"]
            )
        )
        return jsonify(sorted_tasks)
    except Exception as e:
        logging.error(f"Error getting tasks: {str(e)}")
        return jsonify({"error": "Failed to retrieve tasks"}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get("title"):
            return jsonify({"error": "Title is required"}), 400
        
        # Validate priority
        priority = data.get("priority", "medium")
        if priority not in PRIORITY_LEVELS:
            return jsonify({"error": f"Priority must be one of: {', '.join(PRIORITY_LEVELS.keys())}"}), 400
            
        # Create new task
        new_task = {
            "id": str(uuid.uuid4()),
            "title": data["title"],
            "priority": priority,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        tasks.append(new_task)
        return jsonify(new_task), 201
    except Exception as e:
        logging.error(f"Error creating task: {str(e)}")
        return jsonify({"error": "Failed to create task"}), 500

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task"""
    try:
        task = get_task_by_id(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        data = request.get_json()
        
        # Update task fields
        if "title" in data:
            task["title"] = data["title"]
        
        if "priority" in data:
            if data["priority"] not in PRIORITY_LEVELS:
                return jsonify({"error": f"Priority must be one of: {', '.join(PRIORITY_LEVELS.keys())}"}), 400
            task["priority"] = data["priority"]
        
        if "completed" in data:
            task["completed"] = bool(data["completed"])
        
        return jsonify(task)
    except Exception as e:
        logging.error(f"Error updating task: {str(e)}")
        return jsonify({"error": "Failed to update task"}), 500

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        task = get_task_by_id(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        tasks.remove(task)
        return jsonify({"message": "Task deleted successfully"}), 200
    except Exception as e:
        logging.error(f"Error deleting task: {str(e)}")
        return jsonify({"error": "Failed to delete task"}), 500

@app.route('/api/tasks/<task_id>/toggle', methods=['PUT'])
def toggle_task_status(task_id):
    """Toggle the completed status of a task"""
    try:
        task = get_task_by_id(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        task["completed"] = not task["completed"]
        return jsonify(task)
    except Exception as e:
        logging.error(f"Error toggling task status: {str(e)}")
        return jsonify({"error": "Failed to toggle task status"}), 500
