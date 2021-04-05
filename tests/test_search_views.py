"""Search views tests"""

import os
from unittest import TestCase
from models import db, connect_db, User, Trade

os.environ['DATABASE_URL'] = "postgresql:///car-traders-test"

from app import app

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class SearchViewTestCase(TestCase):
    """Test views for search."""

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

    def login(self, client):
        """Helper function that logs in self.u for views that require a login"""

        return client.post('/login',
            data={"username": self.u2.username, "password": "password"},
            follow_redirects=True)

    def test_search_empty(self):
        """Visit search page, but don't input any queries
        - Should return the first 100 trades in the current user's state, sorted by upload time
        """

        with self.client as c:
            self.login(c)
            resp = c.get('/search')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h5 class="card-title">test car 2</h5>', str(resp.data))
            self.assertIn('<h5 class="card-title">test car 3</h5>', str(resp.data))

    def test_search_by_location(self):
        """Visit search page with a location query param
        - Should only return the trades in the passed in query location (just city, just state, or both) 
        """

        with self.client as c:
            self.login(c)

            # search by name of city
            resp = c.get('/search', query_string={"location": "spotswood"})

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h5 class="card-title">test car</h5>', str(resp.data))
            self.assertNotIn('<h5 class="card-title">test car 2</h5>', str(resp.data))
            self.assertNotIn('<h5 class="card-title">test car 3</h5>', str(resp.data))

            # search by name of state
            resp = c.get('/search', query_string={"location": "nj"})

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h5 class="card-title">test car</h5>', str(resp.data))
            self.assertNotIn('<h5 class="card-title">test car 2</h5>', str(resp.data))
            self.assertNotIn('<h5 class="card-title">test car 3</h5>', str(resp.data))

            # search by both
            resp = c.get('/search', query_string={"location": "spotswood, nj"})

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h5 class="card-title">test car</h5>', str(resp.data))
            self.assertNotIn('<h5 class="card-title">test car 2</h5>', str(resp.data))
            self.assertNotIn('<h5 class="card-title">test car 3</h5>', str(resp.data))

    def test_search_by_title(self):
        """Visit search page with a title query param
        - Should only return the trades that contain that query param in their titles AND are located in the current user's state
        """

        with self.client as c:
            self.login(c)

            # Trades 2 & 3 qualify. 1 is not located in user 2's state
            resp = c.get('/search', query_string={"title": "test car"})

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('<h5 class="card-title">test car</h5>', str(resp.data))
            self.assertIn('<h5 class="card-title">test car 2</h5>', str(resp.data))
            self.assertIn('<h5 class="card-title">test car 3</h5>', str(resp.data))


            # Only Trade 2 qualifies
            resp = c.get('/search', query_string={"title": "test car 2"})

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('<h5 class="card-title">test car</h5>', str(resp.data))
            self.assertIn('<h5 class="card-title">test car 2</h5>', str(resp.data))
            self.assertNotIn('<h5 class="card-title">test car 3</h5>', str(resp.data))

    def test_search_by_location_and_title(self):
        """Visit search page with a location & title query params
        - Should only return the trades that contain the title param in their titles AND are located in the passed in location param
        """

        with self.client as c:
            self.login(c)

            # All Trades have "test car" in their titles, but we also specified a location
            # Only Trade 1 now qualifies
            resp = c.get('/search', query_string={
                "title": "test car",
                "location": "spotswood, nj"
            })

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h5 class="card-title">test car</h5>', str(resp.data))
            self.assertNotIn('<h5 class="card-title">test car 2</h5>', str(resp.data))
            self.assertNotIn('<h5 class="card-title">test car 3</h5>', str(resp.data))