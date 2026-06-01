import unittest
import os
import sqlite3
import app as flask_app_module
from app import app, DB_PATH

class FlaskMultiPageBlogTestCase(unittest.TestCase):
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

    def test_feed_empty_state(self):
        # Verify feed page loads successfully without posts
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No stories published yet", response.data)

    def test_create_page_renders(self):
        # Verify the standalone write page serves the publish form successfully
        response = self.client.get('/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Create New Post", response.data)
        self.assertIn(b"Title", response.data)

    def test_publish_and_detail_lifecycle(self):
        # 1. Publish a new post via POST
        publish_response = self.client.post('/create', data=dict(
            title="Deep Dive into Multi-Agent Systems",
            content="Multi-Agent systems communicate securely using decoupled domain APIs."
        ), follow_redirects=True)
        
        self.assertEqual(publish_response.status_code, 200)
        
        # 2. Retrieve post ID securely from SQLite
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute("SELECT id FROM posts WHERE title = 'Deep Dive into Multi-Agent Systems'").fetchone()
        conn.close()
        self.assertIsNotNone(row)
        post_id = row[0]
        
        # 3. Hit GET /post/<id> to assert detailed view compiles successfully
        detail_response = self.client.get(f'/post/{post_id}')
        self.assertEqual(detail_response.status_code, 200)
        self.assertIn(b"Deep Dive into Multi-Agent Systems", detail_response.data)
        self.assertIn(b"Multi-Agent systems communicate securely", detail_response.data)

    def test_delete_post_redirects(self):
        # 1. Create a post to delete
        self.client.post('/create', data=dict(
            title="Post to Delete",
            content="This post will be permanently deleted."
        ))
        
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute("SELECT id FROM posts WHERE title = 'Post to Delete'").fetchone()
        conn.close()
        post_id = row[0]
        
        # 2. Perform DELETE POST request
        delete_response = self.client.post(f'/delete/{post_id}', follow_redirects=True)
        
        # 3. Verify it is deleted and no longer accessible on feed
        self.assertEqual(delete_response.status_code, 200)
        self.assertNotIn(b"Post to Delete", delete_response.data)

    def test_feed_pagination_offsets(self):
        # 1. Insert 6 distinct posts securely
        conn = sqlite3.connect(DB_PATH)
        for i in range(1, 7):
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (f"Blog Post {i}", f"Content {i}"))
        conn.commit()
        conn.close()
        
        # 2. Request page 1 (displays the most recent 5: Blog Post 6 down to Blog Post 2)
        page_1_response = self.client.get('/?page=1')
        self.assertEqual(page_1_response.status_code, 200)
        self.assertIn(b"Blog Post 6", page_1_response.data)
        self.assertIn(b"Blog Post 2", page_1_response.data)
        self.assertNotIn(b"Blog Post 1", page_1_response.data) # 6th post is paginated to page 2!
        
        # 3. Request page 2 (displays the oldest 1: Blog Post 1)
        page_2_response = self.client.get('/?page=2')
        self.assertEqual(page_2_response.status_code, 200)
        self.assertIn(b"Blog Post 1", page_2_response.data)
        self.assertNotIn(b"Blog Post 6", page_2_response.data)

if __name__ == '__main__':
    unittest.main()
