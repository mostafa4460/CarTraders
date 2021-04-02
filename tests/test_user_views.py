"""User views tests"""

# add python path for imports to work
import sys
sys.path.insert(1, '../')

import os
from unittest import TestCase
from models import db, connect_db, User, Trade

os.environ['DATABASE_URL'] = "postgresql:///car-traders-test"

from app import app

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client and add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        u1 = User.signup(
            username="testuser",
            password="password",
            first_name="test",
            last_name="user",
            email="test@test.com",
            phone="7321111111",
            city="Spotswood",
            state="NJ"
        )
        u1.id = 111

        u2 = User.signup(
            username="testuser2",
            password="password",
            first_name="test2",
            last_name="user2",
            email="test2@test2.com",
            phone="7321111112",
            city="San Diego",
            state="CA"
        )
        u2.id = 222

        db.session.commit()

        self.u1 = u1
        self.u2 = u2

        t1 = Trade(
            title="test car",
            user_id= 111
        )

        t2 = Trade(
            title="test car 2",
            user_id= 222
        )

        t3 = Trade(
            title="test car 3",
            user_id= 222
        )

        db.session.add_all([t1, t2, t3])
        db.session.commit()

        self.t1 = t1
        self.t2 = t2

    def tearDown(self):
        """Clean up fouled transactions"""

        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_get_signup(self):
        """Tests the signup form"""

        with self.client as c:
            resp = c.get('/signup')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                '<h1 id="signup-text" class="display-3 text-center mt-5">Create a new account</h1>', str(resp.data)
            )

    def test_post_valid_signup(self):
        """Tests valid user sign up"""

        with self.client as c:
            resp = c.post('/signup', 
                data={
                    "username": "testuser3",
                    "password": "password",
                    "confirm": "password",
                    "first_name": "test",
                    "last_name": "user",
                    "email": "test3@test3.com",
                    "phone": "7321111113",
                    "location": "Spotswood, NJ"
                },
                follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Welcome to CarTraders test', str(resp.data))

    def test_duplicate_username_signup(self):
        """Tests user signup with a username that already exists"""

        with self.client as c:
            resp = c.post('/signup', 
                data={
                    "username": "testuser",
                    "password": "password",
                    "confirm": "password",
                    "first_name": "test",
                    "last_name": "user",
                    "email": "test3@test3.com",
                    "phone": "7321111113",
                    "location": "Spotswood, NJ"
                },
                follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Key (username)=(testuser) already exists.', str(resp.data))

    def test_get_login(self):
        """Tests the login form"""

        with self.client as c:
            resp = c.get('/login')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                '<h1 id="login-text" class="display-3 text-center mt-5">Login</h1>', str(resp.data)
            )

    def test_post_valid_login(self):
        """Tests a valid user login"""

        with self.client as c:
            resp = c.post('/login', 
                data={"username": self.u1.username, "password": "password"},
                follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Welcome back test', str(resp.data))

    def test_post_invalid_login(self):
        """Tests an invalid user login"""

        with self.client as c:
            resp = c.post('/login', 
                data={"username": self.u1.username, "password": "wrongpassword"},
                follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Incorrect Username / Password, please try again.", str(resp.data))

    def login(self, client):
        """Helper function that logs in a user for views that require a login"""

        return client.post('/login',
            data={"username": self.u1.username, "password": "password"},
            follow_redirects=True)

    def test_logout(self):
        """Tests an invalid user login"""

        with self.client as c:
            self.login(c)
            resp = c.post('/logout', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Successfully logged out, please come back soon", str(resp.data))

    def test_profile_loggedin(self):
        """Tests the user profile page, while being logged in"""

        with self.client as c:
            self.login(c)
            resp = c.get('/111')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p class="text-secondary">test@test.com</p>', str(resp.data))
            self.assertIn('<h5 class="card-title">test car</h5>', str(resp.data))
            # visited own profile page, HTML should include EDIT/DELETE buttons
            self.assertIn('<button class="btn btn-danger"><i class="fas fa-trash mr-1"></i>Delete Profile</button>', str(resp.data))

            resp = c.get('/222')
            self.assertEqual(resp.status_code, 200)
            # visited u2's profile page, no EDIT/DELETE buttons
            self.assertNotIn('<button class="btn btn-danger"><i class="fas fa-trash mr-1"></i>Delete Profile</button>', str(resp.data))

    def test_profile_not_loggedin(self):
        """Tests the user profile page, while NOT being logged in"""

        with self.client as c:
            resp = c.get('/111', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in to access this page', str(resp.data))
            self.assertNotIn('<p class="text-secondary">test@test.com</p>', str(resp.data))

    def test_get_edit_form(self):
        """Tests getting the edit form AUTHORIZED / UNAUTHORIZED"""

        with self.client as c:
            self.login(c)

            # UNAUTHORIZED - getting edit form for another user
            resp = c.get('/222/edit', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You are unauthorized to view this page.', str(resp.data))
            self.assertNotIn('<h1 id="edit-text" class="display-3 text-center mt-5">Edit Profile</h1>', str(resp.data))

            # AUTHORIZED
            resp = c.get('/111/edit')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 id="edit-text" class="display-3 text-center mt-5">Edit Profile</h1>', str(resp.data))
            self.assertIn('test@test.com', str(resp.data))

    def test_post_edit_form(self):
        """Tests submitting the edit form"""

        with self.client as c:
            self.login(c)

            resp = c.post('/111/edit', 
                data={"email": "changed@test.com"},
                follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Profile successfully updated', str(resp.data))
            user = User.query.get(111)
            self.assertEqual(user.email, "changed@test.com")

    def test_delete(self):
        """Tests deleting a user AUTHORIZED / UNAUTHORIZED"""

        with self.client as c:
            self.login(c)

            # UNAUTHORIZED - deleting user 222, as user 111
            resp = c.post('/222/delete', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You are unauthorized to perform this action.', str(resp.data))
            user = User.query.get(222)
            self.assertIsNotNone(user)

            # AUTHORIZED
            resp = c.post('/111/delete', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Sorry to see you go testuser, please come back soon', str(resp.data))
            user = User.query.get(111)
            self.assertIsNone(user)