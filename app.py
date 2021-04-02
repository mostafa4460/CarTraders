import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from models import db, connect_db, User, Trade
from forms import UserAddForm, UserEditForm, LoginForm, TradeForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgresql:///car-traders')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "secret")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page"
login_manager.login_message_category = "danger"

connect_db(app)
db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


############################################################
#                         INDEX
############################################################

@app.route('/')
def homepage():
    """Shows the home page:
    
    - anon users: no trades
    - logged in: 100 most recent listings in user's state 
    """

    if current_user.is_authenticated:
        all_trades = (Trade.query
                        .join(User)
                        .filter(User.state == current_user.state)
                        .order_by(Trade.timestamp.desc())
                        .limit(100)
                        .all())
        return render_template("home.html", all_trades=all_trades)

    return render_template("home-anon.html")


############################################################
#                         SEARCH
############################################################

def get_filtered_query(q_obj):
    """A helper function for the search view that takes a query object with possibly multiple query params
    - q_obj = {"q_name": "q_value"}
    - It loops over the query object and only filters the query for the params that were not left blank by the user
    - Returns the resulting query after filtering for all non-empty query params
    """

    loc_q = q_obj["location"]

    trades_query = Trade.query.join(User) if loc_q else Trade.query.join(User).filter(User.state == current_user.state)

    if loc_q:
        trades_query = trades_query.filter(
            (User.city + ', ' + User.state + ', USA').ilike(f'%{loc_q}%')
        )

    for k, v in q_obj.items():
        if v and k != "location":
            trades_query = trades_query.filter(getattr(Trade, k).ilike(f'%{v}%'))

    return (trades_query
            .order_by(Trade.timestamp.desc())
            .limit(100))
            

@app.route('/search')
@login_required
def search():
    """Searches for trades by location and/or the car the user has and/or the car the user wants
    - If the user is logged in, filter the trades by their search and return trades
    - If not logged in, flash msg and redirect to login view (flask-login does this automatically)
    """

    queries = {
        "location": request.args.get("location"), 
        "title": request.args.get("title"),
        "trading_for": request.args.get("trading_for")
    }

    all_trades = get_filtered_query(queries).all()

    return render_template("home.html", all_trades=all_trades)

############################################################
#                        USERS
############################################################

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.
    - If form not valid, present form.
    - If the there already is a user with that username: flash message
    and re-present form.
    """

    if current_user.is_authenticated:
        logout_user()
        flash("Successfully logged out", "success")

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            location = form.location.data.split(',')
            new_user = User.signup(
                username=form.username.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                city=location[0].strip(),
                state=location[1].strip()
            )
            db.session.commit()
            login_user(new_user)
            flash(f"Welcome to CarTraders {new_user.first_name}", "success")
            return redirect(url_for("homepage"))

        except IntegrityError as e:
            flash(e.orig.diag.message_detail, "danger")

    return render_template('users/signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login.
    Check username and password
    - If incorrect login, add error message and re-render form
    - If not, flash success message and redirect to home page.
    """

    if current_user.is_authenticated:
        logout_user()
        flash("Successfully logged out", "success")

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            username = form.username.data,
            password = form.password.data
        )
        if user:
            login_user(user)
            flash(f"Welcome back {user.first_name}", "success")
            return redirect(url_for("homepage"))
        else:
            form.password.errors = ["Incorrect Username / Password, please try again."]
    
    return render_template("users/login.html", form=form)

@app.route('/logout', methods=["POST"])
def logout():
    """Handle user logout.
    - Removes the current_user from the session, then redirects to the login page
    """

    logout_user()
    flash("Successfully logged out, please come back soon", "success")
    return redirect(url_for("login"))

@app.route('/<int:id>')
@login_required
def user_profile(id):
    """Shows the user profile page.
    - If not logged in, flash msg and redirect to login page
    - If logged in, but the profile is not the current user's, don't show Edit/Delete buttons
    - If the profile is the current user's, show Edit/Delete buttons
    """

    user = User.query.get_or_404(id)
    user_trades = Trade.query.join(User).filter(User.id == user.id).all()
    return render_template("users/profile.html", user=user, trades=user_trades)

@app.route('/<int:id>/edit', methods=["GET", "POST"])
@login_required
def edit_user(id):
    """Handle user update.
    - If not logged in, flash msg and redirect to login page
    - If logged in, but the profile is not the current user's, flash different msg and redirect to home
    - If the profile is the current user's, show edit form if get OR update user in DB if post
    """

    user = User.query.get_or_404(id)

    if user.id != current_user.id:
        flash("You are unauthorized to view this page.", "danger")
        return redirect("/")

    form = UserEditForm(obj=user, location=f"{user.city}, {user.state}")

    if form.validate_on_submit():
        location = form.location.data.split(',')
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.phone = form.phone.data
        user.city = location[0].strip()
        user.state = location[1].strip()
        user.cover_pic = form.cover_pic.data or None
        user.profile_pic = form.profile_pic.data or None
        db.session.commit()

        flash("Profile successfully updated", "success")
        return redirect(f"/{user.id}")

    return render_template("users/edit.html", form=form, user=user)

@app.route('/<int:id>/delete', methods=["POST"])
@login_required
def delete_user(id):
    """Handle user deletion.
    - If not logged in, flash msg and redirect to login page
    - If logged in, but the profile is not the current user's, flash different msg and redirect to home
    - If the profile is the current user's, delete the user and all trades owned by user from DB and redirect to login
    """

    user = User.query.get_or_404(id)

    if user.id != current_user.id:
        flash("You are unauthorized to perform this action.", "danger")
        return redirect("/")

    logout_user()

    Trade.query.filter_by(user_id = user.id).delete()
    db.session.delete(user)
    db.session.commit()

    flash(f"Sorry to see you go {user.username}, please come back soon", "info")
    return redirect('/')


############################################################
#                        TRADES
############################################################

@app.route('/trades/new', methods=["GET", "POST"])
@login_required
def add_trade():
    """Add a new trade
    - Show form if get
    - If valid, add trade to DB and redirect to user profile page
    """

    form = TradeForm()

    if form.validate_on_submit():
        trade = Trade(
            title=form.title.data,
            trading_for=form.trading_for.data,
            asking_cash=form.asking_cash.data or None,
            offering_cash=form.offering_cash.data or None,
            img_url=form.img_url.data or None,
            description=form.description.data or None,
            user_id=current_user.id
        )
        db.session.add(trade)
        db.session.commit()
        flash("Successfully added new trade", "success")
        return redirect(f'/{current_user.id}')

    return render_template("trades/add-form.html", form=form)

@app.route('/trades/<int:id>')
@login_required
def get_trade(id):
    """Show the details page for a single trade
    - If not logged in, flash msg and redirect to login page
    - If logged in AND current_user is the owner of the trade, show edit / delete trade buttons
    """

    trade = Trade.query.get_or_404(id)

    return render_template("trades/trade.html", trade=trade)

@app.route('/trades/<int:id>/edit', methods=["GET", "POST"])
@login_required
def edit_trade(id):
    """Handle trade update.
    - If not logged in, flash msg and redirect to login page
    - If logged in, but the profile is not the current user's, flash different msg and redirect to home
    - If the profile is the current user's, show edit form if get OR update trade in DB if post
    """

    trade = Trade.query.get_or_404(id)

    if trade.user.id != current_user.id:
        flash("You are unauthorized to view this page.", "danger")
        return redirect("/")

    form = TradeForm(obj=trade)

    if form.validate_on_submit():
        available = True if request.form["available"] == "True" else False

        trade.title = form.title.data
        trade.trading_for = form.trading_for.data
        trade.asking_cash = form.asking_cash.data
        trade.offering_cash = form.offering_cash.data
        trade.img_url = form.img_url.data
        trade.description = form.description.data
        trade.available = available

        db.session.add(trade)
        db.session.commit()
        flash("Successfully updated trade", "success")
        return redirect(f'/trades/{trade.id}')

    return render_template("trades/edit-form.html", form=form, trade=trade)

@app.route('/trades/<int:id>/delete', methods=["POST"])
@login_required
def delete_trade(id):
    """Handle trade deletion.
    - If not logged in, flash msg and redirect to login page
    - If logged in, but the trade is not the current users', flash different msg and redirect to home
    - If the trade is the current users', delete the trade from the DB and redirect to user's profile page
    """

    trade = Trade.query.get_or_404(id)

    if trade.user.id != current_user.id:
        flash("You are unauthorized to perform this action.", "danger")
        return redirect("/")

    db.session.delete(trade)
    db.session.commit()

    flash("Trade successfully deleted", "info")
    return redirect(f'/{trade.user.id}')