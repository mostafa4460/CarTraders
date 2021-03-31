"""Seed database with sample data."""

from app import db
from models import User, Trade

db.drop_all()
db.create_all()

user1 = User.signup(
    username="moose", 
    password="password", 
    first_name="moose", 
    last_name="nassr", 
    email="email@email.com", 
    phone="7321111111", 
    city="Spotswood", 
    state="NJ"
)

user2 = User.signup(
    username="moose2", 
    password="password2", 
    first_name="moose2", 
    last_name="nassr2", 
    email="email2@email2.com", 
    phone="7321111112", 
    city="Spotswood", 
    state="NJ"
)

user3 = User.signup(
    username="moose3", 
    password="password3", 
    first_name="moose3", 
    last_name="nassr3", 
    email="email3@email3.com", 
    phone="7321111113", 
    city="San Diego", 
    state="CA"
)

db.session.add_all([user1, user2, user3])
db.session.commit()

trade1 = Trade(
    title="2011 Lexus is 250c",
    description="Trading my 2011 Lexus is 250c for a 2014 Audi A4",
    trading_for="2014 Audi A4",
    asking_cash=700,
    user_id=user1.id
)

trade2 = Trade(
    title="2006 Acura MDX",
    description="Trading my 2006 Acura MDX for a 2014 Audi A4",
    trading_for="2014 Audi A4",
    offering_cash=3500,
    user_id=user1.id
)

trade3 = Trade(
    title="2002 Toyota Solara",
    description="Trading my 2002 Toyota Solara for a 2014 Audi A4",
    trading_for="2014 Audi A4",
    offering_cash=6000,
    user_id=user2.id
)

trade4 = Trade(
    title="2014 Hyundai Elantra",
    description="Trading my 2014 Hyundai Elantra for a 2020 Mustang",
    trading_for="2020 Mustang",
    offering_cash=6000,
    user_id=user2.id
)

trade5 = Trade(
    title="2006 Honda Pilot",
    description="Trading my 2006 Honda Pilot. I am open for trades!",
    user_id=user2.id
)

trade6 = Trade(
    title="2015 Kawasaki Ninja 650cc",
    description="Trading my 2015 Kawasaki Ninja 650cc for any truck",
    offering_cash=1000,
    user_id=user1.id
)

trade7 = Trade(
    title="2014 Audi A4",
    description="Trading my 2014 Audi A4 for a 2011 Lexus is 250c",
    trading_for="2011 Lexus is 250c",
    user_id=user1.id
)

trade8 = Trade(
    title="2014 Audi A4",
    description="Trading my 2014 Audi A4 for a 2012 BMW i328",
    trading_for="2012 BMW i328",
    asking_cash=1200,
    user_id=user3.id
)

db.session.add_all([trade1, trade2, trade3, trade4, trade5, trade6, trade7, trade8])
db.session.commit()