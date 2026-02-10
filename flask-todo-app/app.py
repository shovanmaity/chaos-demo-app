"""
In-Memory Todo Application with Auto-Expiration

A Flask web application that stores todos in memory with automatic 5-minute expiration.
"""

import os
import datetime
import json
import threading
import time
from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# In-memory storage for todos
# Structure: {id: {'title': str, 'description': str, 'completed': bool, 'created_at': datetime, 'expires_at': datetime}}
todos_storage = {}
todo_counter = 0
storage_lock = threading.Lock()

# Expiration time in seconds (5 minutes)
EXPIRATION_TIME = 300  # 5 minutes

# Cleanup function to remove expired todos
def cleanup_expired_todos():
    """Background thread to clean up expired todos every 30 seconds."""
    while True:
        time.sleep(30)  # Check every 30 seconds
        now = datetime.datetime.now()
        with storage_lock:
            expired_ids = [
                todo_id for todo_id, todo in todos_storage.items()
                if todo['expires_at'] <= now
            ]
            for todo_id in expired_ids:
                del todos_storage[todo_id]
            if expired_ids:
                print(f"🧹 Cleaned up {len(expired_ids)} expired todo(s)")


# HTML template for the home page with full-featured UI
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Todo App - In-Memory with Auto-Expiration</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --primary: #667eea;
            --primary-dark: #5568d3;
            --secondary: #764ba2;
            --success: #4caf50;
            --danger: #f44336;
            --warning: #ff9800;
            --info: #2196f3;
            --light: #f8f9fa;
            --dark: #333;
            --border: #e0e0e0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            min-height: 100vh;
            padding: 0;
            margin: 0;
        }
        
        /* Header */
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            padding: 20px 0;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .logo-icon {
            font-size: 2em;
        }
        
        .logo-text h1 {
            color: var(--primary);
            font-size: 1.8em;
            font-weight: 700;
            margin: 0;
        }
        
        .logo-text p {
            color: #666;
            font-size: 0.85em;
            margin: 0;
        }
        
        .header-badges {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .badge-success {
            background: var(--success);
            color: white;
        }
        
        .badge-warning {
            background: var(--warning);
            color: white;
        }
        
        .badge-info {
            background: var(--info);
            color: white;
        }
        
        /* Add Todo Form */
        .add-todo-section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
        }
        .add-todo-section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 600;
        }
        .form-group input,
        .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            font-family: inherit;
            transition: border-color 0.3s;
        }
        .form-group input:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        .form-group textarea {
            resize: vertical;
            min-height: 80px;
        }
        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        /* Stats Section */
        .stats-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }
        .stat-card .number {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .stat-card .label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        /* Todos List */
        .todos-section {
            margin-bottom: 30px;
        }
        .todos-section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        .todo-item {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
            gap: 15px;
            transition: all 0.3s;
        }
        .todo-item:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .todo-item.completed {
            opacity: 0.7;
        }
        .todo-checkbox {
            width: 24px;
            height: 24px;
            cursor: pointer;
            margin-top: 3px;
        }
        .todo-content {
            flex: 1;
        }
        .todo-title {
            font-size: 1.2em;
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        .todo-item.completed .todo-title {
            text-decoration: line-through;
            color: #999;
        }
        .todo-description {
            color: #666;
            margin-bottom: 10px;
        }
        .todo-meta {
            font-size: 0.85em;
            color: #999;
        }
        .todo-actions {
            display: flex;
            gap: 10px;
        }
        .btn-small {
            padding: 8px 16px;
            font-size: 0.9em;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-delete {
            background: #f44336;
            color: white;
        }
        .btn-delete:hover {
            background: #d32f2f;
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }
        .empty-state-icon {
            font-size: 4em;
            margin-bottom: 20px;
        }
        
        /* Loading */
        .loading {
            text-align: center;
            padding: 40px;
            color: #667eea;
        }
        
        /* Alert */
        .alert {
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        .alert.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .alert.show {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 Todo App <span class="status-badge">Live</span></h1>
        <p class="subtitle">
            In-memory storage • <span class="warning-badge">⏱️ 5 min expiration</span>
        </p>
        
        <div id="alert" class="alert"></div>
        
        <!-- Stats -->
        <div class="stats-section" id="stats">
            <div class="stat-card">
                <div class="number" id="stat-total">0</div>
                <div class="label">Total</div>
            </div>
            <div class="stat-card">
                <div class="number" id="stat-active">0</div>
                <div class="label">Active</div>
            </div>
            <div class="stat-card">
                <div class="number" id="stat-completed">0</div>
                <div class="label">Completed</div>
            </div>
        </div>
        
        <!-- Add Todo Form -->
        <div class="add-todo-section">
            <h2>➕ Add New Todo</h2>
            <form id="addTodoForm">
                <div class="form-group">
                    <label for="todoTitle">Title *</label>
                    <input type="text" id="todoTitle" placeholder="What needs to be done?" required>
                </div>
                <div class="form-group">
                    <label for="todoDescription">Description</label>
                    <textarea id="todoDescription" placeholder="Add more details..."></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Add Todo</button>
            </form>
        </div>
        
        <!-- Todos List -->
        <div class="todos-section">
            <h2>📋 Your Todos</h2>
            <div id="todosList" class="loading">Loading todos...</div>
        </div>
    </div>

    <script>
        // API Base URL
        const API_BASE = '/api';
        
        // Load todos and stats on page load
        document.addEventListener('DOMContentLoaded', () => {
            loadTodos();
            loadStats();
            
            // Refresh every 10 seconds
            setInterval(() => {
                loadTodos();
                loadStats();
            }, 10000);
        });
        
        // Add todo form submission
        document.getElementById('addTodoForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const title = document.getElementById('todoTitle').value.trim();
            const description = document.getElementById('todoDescription').value.trim();
            
            if (!title) return;
            
            try {
                const response = await fetch(`${API_BASE}/todos`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, description })
                });
                
                if (response.ok) {
                    document.getElementById('todoTitle').value = '';
                    document.getElementById('todoDescription').value = '';
                    showAlert('Todo created successfully!', 'success');
                    loadTodos();
                    loadStats();
                } else {
                    const error = await response.json();
                    showAlert(error.error || 'Failed to create todo', 'error');
                }
            } catch (error) {
                showAlert('Network error: ' + error.message, 'error');
            }
        });
        
        // Load todos
        async function loadTodos() {
            try {
                const response = await fetch(`${API_BASE}/todos`);
                const data = await response.json();
                
                const todosList = document.getElementById('todosList');
                
                if (data.todos.length === 0) {
                    todosList.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-state-icon">📝</div>
                            <p>No todos yet. Create one above!</p>
                        </div>
                    `;
                    return;
                }
                
                todosList.innerHTML = data.todos.map(todo => `
                    <div class="todo-item ${todo.completed ? 'completed' : ''}" data-id="${todo.id}">
                        <input type="checkbox" class="todo-checkbox" 
                               ${todo.completed ? 'checked' : ''} 
                               onchange="toggleTodo(${todo.id})">
                        <div class="todo-content">
                            <div class="todo-title">${escapeHtml(todo.title)}</div>
                            ${todo.description ? `<div class="todo-description">${escapeHtml(todo.description)}</div>` : ''}
                            <div class="todo-meta">
                                ⏱️ Expires in ${formatTime(todo.time_remaining_seconds)}
                            </div>
                        </div>
                        <div class="todo-actions">
                            <button class="btn-small btn-delete" onclick="deleteTodo(${todo.id})">🗑️ Delete</button>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                document.getElementById('todosList').innerHTML = `
                    <div class="empty-state">
                        <p style="color: #f44336;">Error loading todos: ${error.message}</p>
                    </div>
                `;
            }
        }
        
        // Load stats
        async function loadStats() {
            try {
                const response = await fetch(`${API_BASE}/stats`);
                const data = await response.json();
                
                document.getElementById('stat-total').textContent = data.active_todos;
                document.getElementById('stat-active').textContent = data.pending_todos;
                document.getElementById('stat-completed').textContent = data.completed_todos;
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        // Toggle todo completion
        async function toggleTodo(id) {
            try {
                const response = await fetch(`${API_BASE}/todos/${id}/toggle`, {
                    method: 'PATCH'
                });
                
                if (response.ok) {
                    loadTodos();
                    loadStats();
                } else {
                    showAlert('Failed to toggle todo', 'error');
                    loadTodos(); // Reload to reset checkbox
                }
            } catch (error) {
                showAlert('Network error: ' + error.message, 'error');
            }
        }
        
        // Delete todo
        async function deleteTodo(id) {
            if (!confirm('Are you sure you want to delete this todo?')) return;
            
            try {
                const response = await fetch(`${API_BASE}/todos/${id}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    showAlert('Todo deleted successfully!', 'success');
                    loadTodos();
                    loadStats();
                } else {
                    showAlert('Failed to delete todo', 'error');
                }
            } catch (error) {
                showAlert('Network error: ' + error.message, 'error');
            }
        }
        
        // Show alert
        function showAlert(message, type) {
            const alert = document.getElementById('alert');
            alert.textContent = message;
            alert.className = `alert ${type} show`;
            
            setTimeout(() => {
                alert.classList.remove('show');
            }, 3000);
        }
        
        // Format time remaining
        function formatTime(seconds) {
            if (seconds < 0) return 'Expired';
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            return `${mins}m ${secs}s`;
        }
        
        // Escape HTML
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
"""


def serialize_todo(todo_id, todo):
    """Helper function to serialize a todo for JSON response."""
    return {
        'id': todo_id,
        'title': todo['title'],
        'description': todo['description'],
        'completed': todo['completed'],
        'created_at': todo['created_at'].isoformat(),
        'expires_at': todo['expires_at'].isoformat(),
        'time_remaining_seconds': int((todo['expires_at'] - datetime.datetime.now()).total_seconds())
    }


@app.route('/')
def home():
    """Home page with full-featured UI."""
    return render_template('index.html')


@app.route('/api/todos', methods=['GET'])
def getTodos():
    """Get all active (non-expired) todos."""
    now = datetime.datetime.now()
    with storage_lock:
        active_todos = [
            serialize_todo(todo_id, todo)
            for todo_id, todo in todos_storage.items()
            if todo['expires_at'] > now
        ]
    
    return jsonify({
        'todos': active_todos,
        'count': len(active_todos),
        'timestamp': now.isoformat()
    })


@app.route('/api/todos', methods=['POST'])
def createTodo():
    """Create a new todo item."""
    global todo_counter
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    title = data.get('title')
    if not title or not title.strip():
        return jsonify({'error': 'Title is required'}), 400
    
    description = data.get('description', '')
    
    now = datetime.datetime.now()
    expires_at = now + datetime.timedelta(seconds=EXPIRATION_TIME)
    
    with storage_lock:
        todo_counter += 1
        todo_id = todo_counter
        
        todos_storage[todo_id] = {
            'title': title.strip(),
            'description': description.strip(),
            'completed': False,
            'created_at': now,
            'expires_at': expires_at
        }
        
        todo = serialize_todo(todo_id, todos_storage[todo_id])
    
    return jsonify({
        'message': 'Todo created successfully',
        'todo': todo
    }), 201


@app.route('/api/todos/<int:todo_id>', methods=['GET'])
def getTodo(todo_id):
    """Get a specific todo by ID."""
    now = datetime.datetime.now()
    with storage_lock:
        todo = todos_storage.get(todo_id)
        
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404
        
        if todo['expires_at'] <= now:
            return jsonify({'error': 'Todo has expired'}), 410
        
        return jsonify({
            'todo': serialize_todo(todo_id, todo)
        })


@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def updateTodo(todo_id):
    """Update an existing todo."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    now = datetime.datetime.now()
    with storage_lock:
        todo = todos_storage.get(todo_id)
        
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404
        
        if todo['expires_at'] <= now:
            return jsonify({'error': 'Todo has expired'}), 410
        
        # Update fields if provided
        if 'title' in data and data['title']:
            todo['title'] = data['title'].strip()
        
        if 'description' in data:
            todo['description'] = data['description'].strip()
        
        if 'completed' in data and isinstance(data['completed'], bool):
            todo['completed'] = data['completed']
        
        updated_todo = serialize_todo(todo_id, todo)
    
    return jsonify({
        'message': 'Todo updated successfully',
        'todo': updated_todo
    })


@app.route('/api/todos/<int:todo_id>/toggle', methods=['PATCH'])
def toggleTodo(todo_id):
    """Toggle the completed status of a todo."""
    now = datetime.datetime.now()
    with storage_lock:
        todo = todos_storage.get(todo_id)
        
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404
        
        if todo['expires_at'] <= now:
            return jsonify({'error': 'Todo has expired'}), 410
        
        todo['completed'] = not todo['completed']
        updated_todo = serialize_todo(todo_id, todo)
    
    return jsonify({
        'message': f"Todo marked as {'completed' if updated_todo['completed'] else 'incomplete'}",
        'todo': updated_todo
    })


@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def deleteTodo(todo_id):
    """Delete a todo by ID."""
    with storage_lock:
        todo = todos_storage.get(todo_id)
        
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404
        
        del todos_storage[todo_id]
    
    return jsonify({
        'message': 'Todo deleted successfully',
        'id': todo_id
    })


@app.route('/api/stats')
def getStats():
    """Get statistics about todos."""
    now = datetime.datetime.now()
    with storage_lock:
        total = len(todos_storage)
        active = sum(1 for todo in todos_storage.values() if todo['expires_at'] > now)
        expired = total - active
        completed = sum(1 for todo in todos_storage.values() if todo['completed'] and todo['expires_at'] > now)
        pending = active - completed
    
    return jsonify({
        'total_todos': total,
        'active_todos': active,
        'expired_todos': expired,
        'completed_todos': completed,
        'pending_todos': pending,
        'expiration_time_seconds': EXPIRATION_TIME,
        'timestamp': now.isoformat()
    })


@app.route('/health')
def healthStatus():
    """Health check endpoint."""
    with storage_lock:
        todo_count = len(todos_storage)
    
    return jsonify({
        'status': 'healthy',
        'application': 'flask-todo-app',
        'todos_in_memory': todo_count,
        'timestamp': datetime.datetime.now().isoformat()
    })


@app.route('/api/info')
def apiInfo():
    """Get API information and available endpoints."""
    endpoints = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            endpoints.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                'path': str(rule)
            })
    
    return jsonify({
        'application': 'flask-todo-app',
        'version': '1.0.0',
        'data_retention_seconds': EXPIRATION_TIME,
        'endpoints': endpoints
    })


if __name__ == '__main__':
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_expired_todos, daemon=True)
    cleanup_thread.start()
    print(f"🧹 Started background cleanup thread (checks every 30s)")
    
    # Run Flask app
    print(f"\n🚀 Starting In-Memory Todo App...")
    print(f"   📝 Todos expire after {EXPIRATION_TIME} seconds (5 minutes)")
    print(f"   🌐 Visit http://localhost:5000 to see the app\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
