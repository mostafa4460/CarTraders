"""Trade views tests"""

import os
from unittest import TestCase
from models import db, connect_db, User, Trade

os.environ['DATABASE_URL'] = "postgresql:///car-traders-test"

from app import app

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class TradeViewTestCase(TestCase):
    """Test views for trades."""

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
        t1.id = 111

        t2 = Trade(
            title="test car 2",
            user_id= 222
        )
        t2.id = 222

        t3 = Trade(
            title="test car 3",
            user_id= 222
        )
        t3.id = 333

        db.session.add_all([t1, t2, t3])
        db.session.commit()

        self.t1 = t1
        self.t2 = t2
        self.t3 = t3

    def tearDown(self):
        """Clean up fouled transactions"""

        resp = super().tearDown()
        db.session.rollback()
        return resp

    def login(self, client):
        """Helper function that logs in a user for views that require a login"""

        return client.post('/login',
            data={"username": "testuser", "password": "password"},
            follow_redirects=True)

    def test_get_trade_form(self):
        """Tests the get trade form, AUTHORIZED / UNAUTHORIZED"""

        with self.client as c:
            # UNAUTHORIZED - no login
            resp = c.get('/trades/new', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in to access this page', str(resp.data))
            self.assertNotIn('<h1 id="trade-text" class="display-3 text-center mt-5">Create a new trade</h1>', str(resp.data))

            # AUTHORIZED
            self.login(c)
            resp = c.get('/trades/new')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 id="trade-text" class="display-3 text-center mt-5">Create a new trade</h1>', str(resp.data))

    def test_post_trade_form(self):
        """Tests submitting the add trade form"""

        with self.client as c:
            self.login(c)

            resp = c.post('/trades/new', 
                data={
                    "title": "new trade test",
                    "trading_for": "trade test"
                },
                follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Successfully added new trade', str(resp.data))
            trade = Trade.query.filter(Trade.title=='new trade test').first()
            self.assertIsNotNone(trade, str(resp.data))

    def test_trade_details(self):
        """Tests the trade details page AUTHORIZED / UNAUTHORIZED"""

        # UNAUTHORIZED - not logged in
        with self.client as c:
            resp = c.get('/trades/111', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in to access this page', str(resp.data))
            self.assertNotIn('<h2><u>test car</u></h2>', str(resp.data))

        # AUTHORIZED and own trade - page should include EDIT/DELETE buttons
        with self.client as c:
            self.login(c)
            resp = c.get('/trades/111', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2><u>test car</u></h2>', str(resp.data))
            self.assertIn('<button class="btn btn-danger"><i class="fas fa-trash mr-1"></i>Delete Trade</button>', str(resp.data))
            # Trade is available - should not include "SOLD"
            self.assertNotIn("SOLD", str(resp.data))

            # Other user's trade - no EDIT/DELETE buttons
            resp = c.get('/trades/222', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2><u>test car 2</u></h2>', str(resp.data))
            self.assertNotIn('<button class="btn btn-danger"><i class="fas fa-trash mr-1"></i>Delete Trade</button>', str(resp.data))

    def test_get_edit_form(self):
        """Tests getting the edit form AUTHORIZED / UNAUTHORIZED"""

        with self.client as c:
            self.login(c)

            # UNAUTHORIZED - getting edit form for trade owned by another user
            resp = c.get('/trades/222/edit', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You are unauthorized to view this page.', str(resp.data))
            self.assertNotIn('<h1 id="trade-text" class="display-3 text-center mt-5">Edit a trade</h1>', str(resp.data))

            # AUTHORIZED
            resp = c.get('/trades/111/edit')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 id="trade-text" class="display-3 text-center mt-5">Edit a trade</h1>', str(resp.data))
            self.assertIn('test car', str(resp.data))

    def test_post_edit_form(self):
        """Tests submitting the edit form"""

        with self.client as c:
            self.login(c)

            # Change trade availability to False - should now display "SOLD" on trade
            resp = c.post('/trades/111/edit', 
                data={"available": "False"},
                follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Successfully updated trade', str(resp.data))
            self.assertIn('SOLD', str(resp.data))

    def test_delete(self):
        """Tests deleting a trade AUTHORIZED / UNAUTHORIZED"""

        with self.client as c:
            self.login(c)

            # UNAUTHORIZED - deleting trade owned by user 222, as user 111
            resp = c.post('/trades/222/delete', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You are unauthorized to perform this action.', str(resp.data))
            trade = Trade.query.get(222)
            self.assertIsNotNone(trade)

            # AUTHORIZED
            resp = c.post('/trades/111/delete', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Trade successfully deleted', str(resp.data))
            trade = Trade.query.get(111)
            self.assertIsNone(trade)