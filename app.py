import os
import sys
import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for

# ==============================================================================
# 🧪 SRE TROUBLESHOOTER DIAGNOSTIC TOGGLE 1 (Build-time ModuleNotFoundError)
# ------------------------------------------------------------------------------
# To test how the Builder and Troubleshooter identify and root-cause a build-time
# import failure, uncomment the import statement below.
# ==============================================================================
# import non_existent_dependency_module_to_trigger_sre_diagnostics


# ==============================================================================
# 🧪 SRE TROUBLESHOOTER DIAGNOSTIC TOGGLE 2 (Cloud Run Startup Probe Failure)
# ------------------------------------------------------------------------------
# To test how the Deployer detects a failed TCP Startup Probe, triggers the 
# Self-Healing Smart Rollback, and calls the Troubleshooter to diagnose logs,
# uncomment the system exit block below.
# ==============================================================================
# print("[ERROR] Simulated Startup Crash: Port 8080 closed due to unhandled exception.")
# sys.exit(1)


app = Flask(__name__)

# Configure SQLite database path (using writeable /tmp directory for Cloud Run compatibility)
DB_PATH = "/tmp/blog.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema securely at startup."""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the SQLite database schema
init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📝 Premium Serverless Blog Engine</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            --glass-bg: rgba(255, 255, 255, 0.03);
            --glass-border: rgba(255, 255, 255, 0.08);
            --primary-accent: #818cf8;
            --primary-glow: rgba(129, 140, 248, 0.15);
            --danger-accent: #ef4444;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Outfit', sans-serif;
            background: var(--bg-gradient);
            color: #f8fafc;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 60px 20px;
        }
        
        .container {
            max-width: 800px;
            width: 100%;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        h1 {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(to right, #f8fafc, var(--primary-accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }
        
        .subtitle {
            color: #94a3b8;
            font-size: 1rem;
        }
        
        /* Form Styles */
        .form-card {
            background: rgba(255, 255, 255, 0.01);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 40px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #cbd5e1;
            font-size: 0.95rem;
        }
        
        input[type="text"], textarea {
            width: 100%;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--glass-border);
            border-radius: 8px;
            padding: 12px 16px;
            color: #f8fafc;
            font-family: inherit;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus, textarea:focus {
            outline: none;
            border-color: var(--primary-accent);
            box-shadow: 0 0 10px var(--primary-glow);
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: var(--primary-accent);
            color: #0f172a;
            font-weight: 600;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s;
        }
        
        .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 15px var(--primary-glow);
            filter: brightness(1.1);
        }
        
        /* Blog Post list */
        .post-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 28px;
            margin-bottom: 24px;
            position: relative;
            transition: border-color 0.3s;
        }
        
        .post-card:hover {
            border-color: rgba(129, 140, 248, 0.3);
        }
        
        .post-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 10px;
            color: #f8fafc;
        }
        
        .post-meta {
            font-size: 0.85rem;
            color: #64748b;
            margin-bottom: 16px;
        }
        
        .post-content {
            color: #cbd5e1;
            line-height: 1.6;
            font-size: 1.05rem;
            white-space: pre-wrap;
            margin-bottom: 20px;
        }
        
        .btn-danger {
            background: transparent;
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: var(--danger-accent);
            font-weight: 600;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.3s;
        }
        
        .btn-danger:hover {
            background: rgba(239, 68, 68, 0.1);
            border-color: var(--danger-accent);
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #64748b;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Premium Serverless Blog Engine</h1>
            <p class="subtitle">SQLite-powered CRUD blogging module for GCP AutoDeploy verification.</p>
        </header>
        
        <!-- Create Post Section -->
        <section class="form-card">
            <form action="{{ url_for('create_post') }}" method="POST">
                <div class="form-group">
                    <label for="title">Post Title</label>
                    <input type="text" name="title" id="title" placeholder="Enter the title of your post..." required>
                </div>
                <div class="form-group">
                    <label for="content">Content</label>
                    <textarea name="content" id="content" rows="5" placeholder="Write your story here..." required></textarea>
                </div>
                <button type="submit" class="btn">Publish Post</button>
            </form>
        </section>
        
        <!-- Display Posts Section -->
        <section>
            {% if posts %}
                {% for post in posts %}
                    <div class="post-card">
                        <h2 class="post-title">{{ post['title'] }}</h2>
                        <div class="post-meta">Published on {{ post['created_at'] }}</div>
                        <p class="post-content">{{ post['content'] }}</p>
                        <form action="{{ url_for('delete_post', post_id=post['id']) }}" method="POST" onsubmit="return confirm('Are you sure you want to delete this post?');">
                            <button type="submit" class="btn-danger">Delete Post</button>
                        </form>
                    </div>
                {% endfor %}
            {% else: %}
                <div class="empty-state">
                    No stories published yet. Be the first to write one above!
                </div>
            {% endif %}
        </section>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    # Retrieve posts dynamically from SQLite table
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, posts=posts)

@app.route('/create', methods=['POST'])
def create_post():
    # Capture inputs securely
    title = request.form.get('title')
    content = request.form.get('content')
    
    if title and content:
        # Secure Database Access: Use parameterized queries to prevent SQL Injection
        conn = get_db_connection()
        conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
        conn.commit()
        conn.close()
        
    return redirect(url_for('index'))

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    # Secure Database Access: Use parameterized query to safely delete post
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Bind to PORT environment variable (assigned by Cloud Run, defaults to 8080)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
