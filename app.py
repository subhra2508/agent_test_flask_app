import os
import sys
import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, abort

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

# ==============================================================================
# COMMON PREMIUM CSS AND INTERFACE LAYOUT
# ==============================================================================
CSS_STYLE = """
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
        position: relative;
    }
    
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
        padding-bottom: 15px;
        border-bottom: 1px solid var(--glass-border);
    }
    
    .nav-logo {
        font-size: 1.3rem;
        font-weight: 800;
        color: #f8fafc;
        text-decoration: none;
        background: linear-gradient(to right, #f8fafc, var(--primary-accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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
    
    /* Forms */
    .form-group {
        margin-bottom: 24px;
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
        padding: 14px 16px;
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
        text-decoration: none;
        transition: all 0.3s;
    }
    
    .btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px var(--primary-glow);
        filter: brightness(1.1);
    }
    
    .btn-secondary {
        background: transparent;
        border: 1px solid var(--glass-border);
        color: #cbd5e1;
    }
    
    .btn-secondary:hover {
        background: rgba(255, 255, 255, 0.02);
        border-color: #cbd5e1;
        box-shadow: none;
    }
    
    .btn-danger {
        background: transparent;
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: var(--danger-accent);
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .btn-danger:hover {
        background: rgba(239, 68, 68, 0.1);
        border-color: var(--danger-accent);
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2);
    }
    
    /* Blog Feeds */
    .post-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 24px;
        cursor: pointer;
        transition: all 0.3s;
        text-decoration: none;
        display: block;
    }
    
    .post-card:hover {
        border-color: rgba(129, 140, 248, 0.4);
        background: rgba(255, 255, 255, 0.03);
        transform: translateY(-1px);
    }
    
    .post-title {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 10px;
        color: #f8fafc;
    }
    
    .post-meta {
        font-size: 0.85rem;
        color: #64748b;
    }
    
    .post-content-preview {
        color: #cbd5e1;
        line-height: 1.5;
        margin-top: 14px;
        font-size: 0.95rem;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    /* Pagination */
    .pagination {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 40px;
    }
    
    .page-info {
        color: #64748b;
        font-size: 0.95rem;
    }
    
    /* Detail Page */
    .detail-body {
        margin-top: 30px;
        line-height: 1.7;
        font-size: 1.1rem;
        color: #cbd5e1;
        white-space: pre-wrap;
        margin-bottom: 40px;
    }
    
    .actions-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid var(--glass-border);
        padding-top: 24px;
    }
    
    .empty-state {
        text-align: center;
        padding: 50px 20px;
        color: #64748b;
        font-style: italic;
    }
</style>
"""

# ==============================================================================
# VIEW TEMPLATES
# ==============================================================================

INDEX_TEMPLATE = CSS_STYLE + """
<div class="container">
    <nav class="nav-bar">
        <a href="{{ url_for('index') }}" class="nav-logo">📝 Serverless Blog</a>
        <a href="{{ url_for('create_page') }}" class="btn">+ New Post</a>
    </nav>
    
    <header>
        <h1>Blogging Feed</h1>
        <p class="subtitle">Stateless SQLite-powered pagination feed.</p>
    </header>
    
    <section>
        {% if posts %}
            {% for post in posts %}
                <a href="{{ url_for('post_detail', post_id=post['id']) }}" class="post-card">
                    <h2 class="post-title">{{ post['title'] }}</h2>
                    <div class="post-meta">Published on {{ post['created_at'] }}</div>
                    <p class="post-content-preview">{{ post['content'] }}</p>
                </a>
            {% endfor %}
        {% else: %}
            <div class="empty-state">
                No stories published yet. Click "+ New Post" to write the first one!
            </div>
        {% endif %}
    </section>
    
    <!-- Pagination Controls -->
    {% if total_pages > 1 %}
        <div class="pagination">
            {% if page > 1 %}
                <a href="{{ url_for('index', page=page-1) }}" class="btn btn-secondary">← Previous</a>
            {% else: %}
                <div></div>
            {% endif %}
            
            <span class="page-info">Page {{ page }} of {{ total_pages }}</span>
            
            {% if page < total_pages %}
                <a href="{{ url_for('index', page=page+1) }}" class="btn btn-secondary">Next →</a>
            {% else: %}
                <div></div>
            {% endif %}
        </div>
    {% endif %}
</div>
"""

CREATE_TEMPLATE = CSS_STYLE + """
<div class="container">
    <nav class="nav-bar">
        <a href="{{ url_for('index') }}" class="nav-logo">📝 Serverless Blog</a>
        <a href="{{ url_for('index') }}" class="btn btn-secondary">← Feed</a>
    </nav>
    
    <header>
        <h1>Create New Post</h1>
        <p class="subtitle">Share your story with the world.</p>
    </header>
    
    <form action="{{ url_for('create_post') }}" method="POST">
        <div class="form-group">
            <label for="title">Title</label>
            <input type="text" name="title" id="title" placeholder="Give your story a title..." required>
        </div>
        <div class="form-group">
            <label for="content">Content</label>
            <textarea name="content" id="content" rows="10" placeholder="Once upon a time..." required></textarea>
        </div>
        <button type="submit" class="btn">Publish Post</button>
    </form>
</div>
"""

DETAIL_TEMPLATE = CSS_STYLE + """
<div class="container">
    <nav class="nav-bar">
        <a href="{{ url_for('index') }}" class="nav-logo">📝 Serverless Blog</a>
        <a href="{{ url_for('index') }}" class="btn btn-secondary">← Back to Feed</a>
    </nav>
    
    <article>
        <h1>{{ post['title'] }}</h1>
        <div class="post-meta" style="margin-top: 10px;">Published on {{ post['created_at'] }}</div>
        <div class="detail-body">{{ post['content'] }}</div>
    </article>
    
    <div class="actions-bar">
        <a href="{{ url_for('index') }}" class="btn btn-secondary">Back</a>
        <form action="{{ url_for('delete_post', post_id=post['id']) }}" method="POST" onsubmit="return confirm('Are you sure you want to delete this post permanently?');">
            <button type="submit" class="btn-danger">Delete Article</button>
        </form>
    </div>
</div>
"""

# ==============================================================================
# APPLICATION ROUTES & ENDPOINTS
# ==============================================================================

@app.route('/')
def index():
    # Paginate posts (5 articles per page)
    page = request.args.get('page', 1, type=int)
    limit = 5
    offset = (page - 1) * limit
    
    conn = get_db_connection()
    # Count total posts dynamically
    total_posts_row = conn.execute('SELECT COUNT(*) FROM posts').fetchone()
    total_posts = total_posts_row[0] if total_posts_row else 0
    
    # Retrieve paginated rows securely using database limits
    posts = conn.execute(
        'SELECT * FROM posts ORDER BY id DESC LIMIT ? OFFSET ?', 
        (limit, offset)
    ).fetchall()
    conn.close()
    
    total_pages = (total_posts + limit - 1) // limit
    
    return render_template_string(
        INDEX_TEMPLATE, 
        posts=posts, 
        page=page, 
        total_pages=total_pages
    )

@app.route('/create', methods=['GET'])
def create_page():
    return render_template_string(CREATE_TEMPLATE)

@app.route('/create', methods=['POST'])
def create_post():
    title = request.form.get('title')
    content = request.form.get('content')
    
    if title and content:
        # Secure database access parameterized SQL
        conn = get_db_connection()
        conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
        conn.commit()
        conn.close()
        
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>', methods=['GET'])
def post_detail(post_id):
    # Fetch post securely by ID
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    
    if not post:
        abort(404, description="Post not found")
        
    return render_template_string(DETAIL_TEMPLATE, post=post)

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    # Secure Database Access parameterized SQL delete
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Bind to PORT environment variable (assigned by Cloud Run, defaults to 8080)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
