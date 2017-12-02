import os
import re
import datetime
from cs50 import SQL
from flask import Flask, redirect, flash, jsonify, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, apology, usd, area

# Configure application
app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///aparkments.db")

# Custom filter
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["area"] = area

# Ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.route("/")
# @login_required
def index():
    """Render map"""
    if not os.environ.get("API_KEY"):
        raise RuntimeError("API_KEY not set")
    return render_template("index.html", key=os.environ.get("API_KEY"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirm password was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide confirm password", 400)

        # Ensure confirm password was submitted
        if request.form.get("confirmation") != request.form.get("password"):
            return apology("confirm password must match password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username does not exist
        if rows:
            return apology("username already exists", 400)

        # Get passward
        plainpassword = request.form.get("password")

        # Insert database with username and password
        rows = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                          username=request.form.get("username"), hash=generate_password_hash(plainpassword))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/info")
def info():
    """Look up info for geo"""

    # Get location input
    geo = request.args.get("geo")

    # Ensure location input is entered
    if not geo:
        raise RuntimeError("geo not found")

    # Get all information for parking facility with key: geo
    binfo = db.execute("SELECT * FROM parking WHERE key = :k", k=geo)

    # Return info as JSON onjects
    return jsonify(binfo)


@app.route("/search")
def search():
    """Search for parking facilities that match query"""

    # Get location input
    q = request.args.get("q") + "%"

    # Get info from parking for those close to location input
    location = db.execute(
        "SELECT * FROM parking WHERE Address LIKE :q OR ZipCode LIKE :q", q=q)

    # Keep only up to 10 locations
    if len(location) > 10:
        location = [location[0], location[1], location[2],  location[3], location[4],
                    location[5], location[6],  location[7],  location[8],  location[9]]

    # Return places as JSON onjects
    return jsonify(location)


@app.route("/update")
def update():
    """Find up to 10 parkings within view"""

    # Ensure parameters are present
    if not request.args.get("sw"):
        raise RuntimeError("missing sw")
    if not request.args.get("ne"):
        raise RuntimeError("missing ne")

    # Ensure parameters are in lat,lng format
    if not re.search("^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$", request.args.get("sw")):
        raise RuntimeError("invalid sw")
    if not re.search("^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$", request.args.get("ne")):
        raise RuntimeError("invalid ne")

    # Explode southwest corner into two variables
    sw_lat, sw_lng = map(float, request.args.get("sw").split(","))

    # Explode northeast corner into two variables
    ne_lat, ne_lng = map(float, request.args.get("ne").split(","))

    # Find 10 pakrings within view, pseudorandomly chosen if more within view
    if sw_lng <= ne_lng:

        # Doesn't cross the antimeridian
        rows = db.execute("""SELECT * FROM parking
                          WHERE :sw_lat <= lat AND lat <= :ne_lat AND (:sw_lng <= lng AND lng <= :ne_lng)
                          ORDER BY RANDOM()
                          LIMIT 10""",
                          sw_lat=sw_lat, ne_lat=ne_lat, sw_lng=sw_lng, ne_lng=ne_lng)

    else:

        # Crosses the antimeridian
        rows = db.execute("""SELECT * FROM parking
                          WHERE :sw_lat <= lat AND lat <= :ne_lat AND (:sw_lng <= lng OR lng <= :ne_lng)
                          ORDER BY RANDOM()
                          LIMIT 10""",
                          sw_lat=sw_lat, ne_lat=ne_lat, sw_lng=sw_lng, ne_lng=ne_lng)

    # Output places as JSON
    return jsonify(rows)


@app.route("/convert", methods=["GET", "POST"])
@login_required
def convert():
    """Parse location key"""

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("convert.html")

    # Get the location key and parse to convert.html
    else:
        skey = request.form["skey"]
        return render_template("convert.html", skey=skey)


@app.route("/convertagain", methods=["GET", "POST"])
@login_required
def convertagain():
    """Parse same location key"""

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("convert.html")

    # Get the location key and parse to convert.html
    else:
        skey = request.form.get("sekey")
        return render_template("convert.html", skey=skey)



@app.route("/calculate", methods=["GET", "POST"])
@login_required
def calculate():
    """Calculate total price"""

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("convert.html")

    else:

        # Get location key
        skey = request.form.get("sekey")

        # Select info for location key
        row = db.execute("SELECT * FROM parking WHERE key = :a", a=skey)

        # Get price per sqft for location key
        unitprice = row[0]["Price_per_sqft"]

        # Get building area for location key
        area = row[0]["BldgArea"]

        # If building area is zero, use lot size to calculate building area
        if area == "0" and row[0]["NumFloors"] != 0:
            area = row[0]["SHAPE_Area"]* row[0]["NumFloors"]

        # If number of floors is zero, use user's input to calculate building area
        if row[0]["NumFloors"] == 0:
            numf = float(request.form["num_f"])
            area = row[0]["SHAPE_Area"] *numf

        # Convet percentage input to 2 decimals
        pcta = int(request.form.get("pct_a")) * 0.01
        pctb = int(request.form.get("pct_b")) * 0.01
        pctc = int(request.form.get("pct_c")) * 0.01

        # Get unit size for each unit type
        areaa = db.execute("SELECT area FROM unittype WHERE type = :u", u="Studio")
        areab = db.execute("SELECT area FROM unittype WHERE type = :u", u="One bedroom")
        areac = db.execute("SELECT area FROM unittype WHERE type = :u", u="Two bedroom")

        # Calculate numbers of units that matching the percentage input
        numa = int( (area * pcta) / areaa[0]["area"] )
        numb = int( (area * pctb) / areab[0]["area"] )
        numc = int( (area * pctc) / areac[0]["area"] )

        # Calcualte total price
        totalprice = (numa * areaa[0]["area"] + numb * areab[0]["area"] + numc * areac[0]["area"]) * unitprice

        # Add the input and calculation to history
        db.execute("INSERT INTO history (id, Address, BldgArea, Studio, One_bedroom, Two_bedroom, Totalprice) VALUES (:uid, :address, :ba, :s, :one, :two, :total)",
                   uid=session["user_id"], address=row[0]["Address"], ba=area, s=numa, one=numb, two=numc, total=totalprice)

        # Display input and calculation on calculate.html
        return render_template("calculate.html", total=totalprice, p=row[0]["Address"], barea=area, a=numa, b=numb, c=numc, key=skey)


@app.route("/history")
@login_required
def history():
    """Show history of calculations"""

    # Query database of history for user id
    calculations = db.execute("SELECT * FROM history WHERE id = :uid", uid=session["user_id"])

    # Display details of all calculations of the user
    return render_template("history.html", calculations=calculations)


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
