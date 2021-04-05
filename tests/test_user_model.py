"""User model tests"""

import os
from unittest import TestCase
from models import db, connect_db, User
from sqlalchemy import exc

os.environ['DATABASE_URL'] = "postgresql:///car-traders-test"

from app import app

db.create_all()


class UserModelTestCase(TestCase):
    """Tests for user model."""

    def setUp(self):
        """Clean up data and add sample data"""

        db.drop_all()
        db.create_all()

        u1 = User.signup(
            username="testuser1",
            password="password",
            first_name="test",
            last_name="user",
            email="test1@1test.com",
            phone="7321111110",
            city="Spotswood",
            state="NJ"
        )
        u1.id = 999

        db.session.commit()
        self.u1 = u1

    def tearDown(self):
        """Clean up fouled transactions"""

        res = super().tearDown()
        db.session.rollback()
        return res

    #####################################
    #           Signup Tests
    #####################################

    def test_valid_signup(self):
        """Signup, everything fine"""

        user = User.signup(
            username="testuser",
            password="password",
            first_name="test",
            last_name="user",
            email="test@test.com",
            phone="7321111111",
            city="Spotswood",
            state="NJ"
        )
        user.id = 111
        db.session.commit()

        user = User.query.get(111)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@test.com")
        self.assertNotEqual(user.password, "password")

    def test_invalid_username_signup(self):
        """Signup, left username field blank"""

        user = User.signup(
            username=None,
            password="password",
            first_name="test",
            last_name="user",
            email="test2@test2.com",
            phone="7321111112",
            city="Spotswood",
            state="NJ"
        )
        user.id = 222
        
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_phone_signup(self):
        """Signup, left phone field blank"""

        user = User.signup(
            username="testuser3",
            password="password",
            first_name="test",
            last_name="user",
            email="test3@test3.com",
            phone=None,
            city="Spotswood",
            state="NJ"
        )
        user.id = 333
        
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    #####################################
    #       Authentication Tests
    #####################################

    def test_valid_auth(self):
        """Login, everything is fine"""

        user = User.authenticate(username=self.u1.username, password="password")

        self.assertIsNotNone(user)
        self.assertEqual(user.phone, "7321111110")

    def test_invalid_username(self):
        """Login, wrong username"""

        user = User.authenticate(username="badusername", password="password")
        self.assertFalse(user)

    def test_wrong_password(self):
        """Login, wrong password"""

        user = User.authenticate(username=self.u1.username, password="wrongpassword")
        self.assertFalse(user)