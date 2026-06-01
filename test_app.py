import unittest
import os
import sqlite3
import app as flask_app_module
from app import app, DB_PATH

class FlaskBlogTestCase(unittest.TestCase):
    def setUp(self):
        # Configure testing environment
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Wipe any previous test database to start fresh
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            
        # Initialize database schema securely for testing
        flask_app_module.init_db()

    def tearDown(self):
        # Clean up database file after test suite runs
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

    def test_index_empty_state(self):
        # Verify index route loads successfully without posts
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No stories published yet", response.data)

    def test_create_and_display_post(self):
        # Securely publish a new post via POST request
        response = self.client.post('/create', data=dict(
            title="My Agent Verification Post",
            content="This blog post verifies SQLite integrations function successfully!"
        ), follow_redirects=True)
        
        # Verify it redirects to home page and lists the new post
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"My Agent Verification Post", response.data)
        self.assertIn(b"This blog post verifies SQLite integrations", response.data)

    def test_delete_post(self):
        # 1. Create a post to get an active ID
        self.client.post('/create', data=dict(
            title="Temporary Post to Delete",
            content="This content will be removed."
        ))
        
        # Fetch post id directly from SQLite
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute("SELECT id FROM posts WHERE title = 'Temporary Post to Delete'").fetchone()
        conn.close()
        
        self.assertIsNotNone(row, "Post creation failed during delete test setup.")
        post_id = row[0]
        
        # 2. Execute POST delete request
        delete_response = self.client.post(f'/delete/{post_id}', follow_redirects=True)
        
        # 3. Verify post is deleted and no longer displayed on home page
        self.assertEqual(delete_response.status_code, 200)
        self.assertNotIn(b"Temporary Post to Delete", delete_response.data)
        self.assertIn(b"No stories published yet", delete_response.data)

if __name__ == '__main__':
    unittest.main()
