import os
import re
from cs50 import SQL
from flask import Flask, jsonify, render_template, request, session
from flask_session import Session


from helpers import login_required, apology, lookup

# Configure application
app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///mashup.db")


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """Render map"""
    if not os.environ.get("API_KEY"):
        raise RuntimeError("API_KEY not set")
    return render_template("index.html", key=os.environ.get("API_KEY"))


# @app.route("/articles")
# def articles():
#     """Look up articles for geo"""
#     # TODO
#     geo = request.args.get("geo")

#     if not geo:
#         raise RuntimeError("geo not found")

#     articles = lookup(geo)

#     if len(articles) > 5:
#         articles = [articles[0], articles[1], articles[2], articles[3], articles[4]]

#     return jsonify(articles)


@app.route("/search")
def search():
    """Search for places that match query"""

    q = request.args.get("q") + "%"

    location = db.execute(
        "SELECT * FROM parking WHERE Address LIKE :q OR ZipCode LIKE :q", q=q)
    # print(location)

    if len(location) > 10:
        location = [location[0], location[1], location[2],  location[3], location[4],
                    location[5], location[6],  location[7],  location[8],  location[9]]

    # print(location)

    return jsonify(location)


@app.route("/update")
def update():
    """Find up to 10 places within view"""

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

    # Find 10 cities within view, pseudorandomly chosen if more within view
    if sw_lng <= ne_lng:

        # Doesn't cross the antimeridian
        rows = db.execute("""SELECT * FROM parking
                          WHERE :sw_lat <= lat AND lat <= :ne_lat AND (:sw_lng <= lng AND lng <= :ne_lng)
                        #   GROUP BY country_code, place_name, admin_code1
                          ORDER BY RANDOM()
                          LIMIT 10""",
                          sw_lat=sw_lat, ne_lat=ne_lat, sw_lng=sw_lng, ne_lng=ne_lng)

    else:

        # Crosses the antimeridian
        rows = db.execute("""SELECT * FROM parking
                          WHERE :sw_lat <= lat AND lat <= :ne_lat AND (:sw_lng <= lng OR lng <= :ne_lng)
                        #   GROUP BY country_code, place_name, admin_code1
                          ORDER BY RANDOM()
                          LIMIT 10""",
                          sw_lat=sw_lat, ne_lat=ne_lat, sw_lng=sw_lng, ne_lng=ne_lng)

    # Output places as JSON
    return jsonify(rows)








# @app.route("/")
# @login_required
# def index():
#     """Show portfolio of stocks"""

#     symbol_shares = db.execute(
#         "SELECT symbol,shares,name,total,price FROM portfolio WHERE id = :id", id=session["user_id"])
#     cash_now = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])

#     # total amout
#     # total for different shares
#     total_shares = 0
#     for i in symbol_shares:
#         total = i["total"]
#         total_shares = total_shares + total

#     total_final = cash_now[0]["cash"] + total_shares
#     return render_template("index.html", stocks=symbol_shares, cash=cash_now[0]["cash"], total=total_final)


# @app.route("/buy", methods=["GET", "POST"])
# @login_required
# def buy():
#     """Buy shares of stock"""

#     if request.method == "GET":
#         return render_template("buy.html")

#     else:
#         # get the dictionary stock
#         stock = lookup(request.form.get("symbol"))

#         # Check if stock is valid
#         if not stock:
#             return apology("Symbol does not exist.")

#         # Check if the shares is a positive integer
#         # check non-numeric
#         try:
#             shares = float(request.form.get("shares"))
#         except ValueError:
#             return apology("Share is not a positive integer")

#         # check negative
#         if shares < 0:
#             return apology("Share is not a positive integer")

#         # check fraction
#         if shares - round(shares) != 0:
#             return apology("Share is not a positive integer")

#         # check if user could afford the stock
#         money_you_have = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])
#         if not money_you_have or money_you_have[0]["cash"] < stock["price"] * shares:
#             return apology("Money is not enough to buy shares")

#          # Get time
#         occrent_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

#         # Write in history
#         db.execute("INSERT INTO history (id, symbol, shares, price, transacted) VALUES( :id, :symbol, :shares, :price, :transacted)",
#                   id=session["user_id"], symbol=stock["symbol"], price=stock["price"], shares=shares, transacted=occrent_time)

#         # buy more of the same stock
#         original_shares = db.execute(
#             "SELECT shares FROM portfolio WHERE id = :id AND symbol = :symbol", id=session["user_id"], symbol=stock["symbol"])

#         if not original_shares:
#             # Add stock to user's portfolio
#             db.execute("INSERT INTO portfolio (id, price, symbol, shares,name, total ) VALUES(:id, :price, :symbol, :shares, :name, :total)",
#                       id=session["user_id"], symbol=stock["symbol"], price=stock["price"], name=stock["symbol"], shares=shares, total=stock["price"] * shares)

#         else:
#             original_total = db.execute(
#                 " SELECT total FROM portfolio WHERE id = :id AND symbol = :symbol", id=session["user_id"], symbol=stock["symbol"])
#             db.execute("UPDATE portfolio SET shares =:share, total= :total WHERE id = :id AND symbol =:symbol",
#                       id=session["user_id"], symbol=stock["symbol"], share=shares + original_shares[0]["shares"], total=stock["price"] * shares + original_total[0]["total"])

#         # Update cash
#         db.execute("UPDATE users SET cash = cash - :buy WHERE id = :id",
#                   buy=stock['price'] * shares, id=session["user_id"])

#         return redirect("/")


# @app.route("/history")
# @login_required
# def history():
#     """Show history of transactions"""

#     symbol_shares = db.execute(
#         "SELECT id, symbol, shares, price, transacted FROM history WHERE id = :id", id=session["user_id"])
#     return render_template("history.html", stocks=symbol_shares)


# @app.route("/login", methods=["GET", "POST"])
# def login():
#     """Log user in"""

#     # Forget any user_id
#     session.clear()

#     # User reached route via POST (as by submitting a form via POST)
#     if request.method == "POST":

#         # Ensure username was submitted
#         if not request.form.get("username"):
#             return apology("must provide username", 403)

#         # Ensure password was submitted
#         elif not request.form.get("password"):
#             return apology("must provide password", 403)

#         # Query database for username
#         rows = db.execute("SELECT * FROM users WHERE username = :username",
#                           username=request.form.get("username"))

#         # Ensure username exists and password is correct
#         if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
#             return apology("invalid username and/or password", 403)

#         # Remember which user has logged in
#         session["user_id"] = rows[0]["id"]

#         # Redirect user to home page
#         return redirect("/")

#     # User reached route via GET (as by clicking a link or via redirect)
#     else:
#         return render_template("login.html")


# @app.route("/logout")
# def logout():
#     """Log user out"""
#     # Forget any user_id
#     session.clear()
#     # Redirect user to login form
#     return redirect("/")


# @app.route("/quote", methods=["GET", "POST"])
# @login_required
# def quote():
#     """Get stock quote."""

#     # Get the symbol
#     if request.method == "POST":
#         rows = lookup(request.form.get("symbol"))

#         if not rows:
#             return apology("Invalid Symbol")

#         return render_template("quoted.html", stock=rows)

#     else:
#         return render_template("quote.html")


# @app.route("/register", methods=["GET", "POST"])
# def register():
#     """Register user"""

#     # User reached route via POST (as by submitting a form via POST)
#     if request.method == "POST":

#         # Ensure username was submitted
#         if not request.form.get("username"):
#             return apology("Missing username", 400)

#         # Ensure password was submitted
#         elif not request.form.get("password"):
#             return apology("Missing password", 400)

#         # Ensure password was submitted
#         elif not request.form.get("confirmation"):
#             return apology("Missing password confirmation", 400)

#         # Ensure password and confirmation match
#         if request.form.get("password") != request.form.get("confirmation"):
#             return apology("password and confirmation don't match", 400)

#         # Hash password
#         password = request.form.get("password")

#         result = db.execute("INSERT INTO users(username, hash) VALUES(:username, :hash)",
#                             username=request.form.get("username"), hash=generate_password_hash(password))

#         if not result:
#             return apology("User already exist")

#         #  Keep user login
#         session["user_id"] = result

#         # Redirect user to home page
#         return redirect("/")
#     else:
#         return render_template("register.html")


@app.route("/calculate", methods=["GET", "POST"])
#@login_required
def sell():
    """Calculate Value"""

    if request.method == "GET":
        return render_template("calculate.html")

    else:
        row = db.execute("SELECT * FROM parking WHERE Address = :a", a=session["Address"])

        unitprice = row["Price_per_sqft"]

        area = row["BldgArea"]

        # Manhattan setback requirements: avg. 15ft
        if area == "0" and row["NumFloors"] != 0:
            area = (row["SHAPE_Area"] - row["SHAPE_Leng"] * 15 ) * row["NumFloors"]

        if row["NumFloors"] == 0:
            numf = request.form.get("num_f")
            area = (row["SHAPE_Area"] - row["SHAPE_Leng"] * 15 ) * numf

        # Ensure input is positive integer
        if not request.form.get("pct_a").isdigit() or int(request.form.get("pct_a")) <= 0:
            return apology("input must be positive integer", 400)
        if not request.form.get("pct_b").isdigit() or int(request.form.get("pct_b")) <= 0:
            return apology("input must be positive integer", 400)
        if not request.form.get("pct_c").isdigit() or int(request.form.get("pct_c")) <= 0:
            return apology("input must be positive integer", 400)

        # scroll down menu should be 0-100 for pct_a, 0-remaining for pct_b, 0-remaning for pct_c

        pcta = request.form.get("pct_a") * 0.01
        unita = request.form.get("unit_a")
        pctb = request.form.get("pct_b") * 0.01
        unitb = request.form.get("unit_b")
        pctc = request.form.get("pct_c") * 0.01
        unitc = request.form.get("unit_c")

        areaa = db.execute("SELECT area FROM unittype WHERE type = :u", u="Studio")
        areab = db.execute("SELECT area FROM unittype WHERE type = :u", u="One bedroom")
        areac = db.execute("SELECT area FROM unittype WHERE type = :u", u="Two bedroom")

        numa = int( (area * pcta) / areaa )
        numb = int( (area * pctb) / areab )
        numc = int( (area * pctc) / areac )

        totalprice = (numa * areaa + numb * areab + numc * areac) * unitprice

        return render_template("calculate.html", stocks=stocks, utotal=total, balance=balance[0]['cash'])


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
