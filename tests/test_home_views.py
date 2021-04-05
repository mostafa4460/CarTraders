"""Home page views tests"""

import os
from unittest import TestCase
from models import db, connect_db, User

os.environ['DATABASE_URL'] = "postgresql:///car-traders-test"

from app import app

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class HomeViewTestCase(TestCase):
    """Test views for home page."""

    def setUp(self):
        """Create test client and add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        u = User.signup(
            username="testuser",
            password="password",
            first_name="test",
            last_name="user",
            email="test@test.com",
            phone="7321111110",
            city="Spotswood",
            state="NJ"
        )
        u.id = 111
        db.session.commit()

        self.u = u

    def tearDown(self):
        """Clean up fouled transactions"""

        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_home_no_user(self):
        """Visit home page with no users logged in"""

        with self.client as c:
            resp = c.get('/')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2 class="display-5"><b>Start Trading Cars Now</b></h2>', str(resp.data))

    def login(self, client):
        """Helper function that logs in self.u for views that require a login"""

        return client.post('/login',
                data={"username": self.u.username, "password": "password"},
                follow_redirects=True)

    def test_home_with_user(self):
        """Visit home page with a user logged in"""

        with self.client as c: 
            self.login(c)               
            resp = c.get('/')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<form class="mx-auto mt-4" action="/search">', str(resp.data))