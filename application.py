from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from time import gmtime, strftime
from helpers import apology, login_required, lookup, usd

##jdjdjdjdj

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    symbol_shares = db.execute(
        "SELECT symbol,shares,name,total,price FROM portfolio WHERE id = :id", id=session["user_id"])
    cash_now = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])

    # total amout
    # total for different shares
    total_shares = 0
    for i in symbol_shares:
        total = i["total"]
        total_shares = total_shares + total

    total_final = cash_now[0]["cash"] + total_shares
    return render_template("index.html", stocks=symbol_shares, cash=cash_now[0]["cash"], total=total_final)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "GET":
        return render_template("buy.html")

    else:
        # get the dictionary stock
        stock = lookup(request.form.get("symbol"))

        # Check if stock is valid
        if not stock:
            return apology("Symbol does not exist.")

        # Check if the shares is a positive integer
        # check non-numeric
        try:
            shares = float(request.form.get("shares"))
        except ValueError:
            return apology("Share is not a positive integer")

        # check negative
        if shares < 0:
            return apology("Share is not a positive integer")

        # check fraction
        if shares - round(shares) != 0:
            return apology("Share is not a positive integer")

        # check if user could afford the stock
        money_you_have = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])
        if not money_you_have or money_you_have[0]["cash"] < stock["price"] * shares:
            return apology("Money is not enough to buy shares")

         # Get time
        occrent_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

        # Write in history
        db.execute("INSERT INTO history (id, symbol, shares, price, transacted) VALUES( :id, :symbol, :shares, :price, :transacted)",
                  id=session["user_id"], symbol=stock["symbol"], price=stock["price"], shares=shares, transacted=occrent_time)

        # buy more of the same stock
        original_shares = db.execute(
            "SELECT shares FROM portfolio WHERE id = :id AND symbol = :symbol", id=session["user_id"], symbol=stock["symbol"])

        if not original_shares:
            # Add stock to user's portfolio
            db.execute("INSERT INTO portfolio (id, price, symbol, shares,name, total ) VALUES(:id, :price, :symbol, :shares, :name, :total)",
                      id=session["user_id"], symbol=stock["symbol"], price=stock["price"], name=stock["symbol"], shares=shares, total=stock["price"] * shares)

        else:
            original_total = db.execute(
                " SELECT total FROM portfolio WHERE id = :id AND symbol = :symbol", id=session["user_id"], symbol=stock["symbol"])
            db.execute("UPDATE portfolio SET shares =:share, total= :total WHERE id = :id AND symbol =:symbol",
                       id=session["user_id"], symbol=stock["symbol"], share=shares + original_shares[0]["shares"], total=stock["price"] * shares + original_total[0]["total"])

        # Update cash
        db.execute("UPDATE users SET cash = cash - :buy WHERE id = :id",
                   buy=stock['price'] * shares, id=session["user_id"])

        return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    symbol_shares = db.execute(
        "SELECT id, symbol, shares, price, transacted FROM history WHERE id = :id", id=session["user_id"])
    return render_template("history.html", stocks=symbol_shares)


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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # Get the symbol
    if request.method == "POST":
        rows = lookup(request.form.get("symbol"))

        if not rows:
            return apology("Invalid Symbol")

        return render_template("quoted.html", stock=rows)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Missing username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Missing password", 400)

        # Ensure password was submitted
        elif not request.form.get("confirmation"):
            return apology("Missing password confirmation", 400)

        # Ensure password and confirmation match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation don't match", 400)

        # Hash password
        password = request.form.get("password")

        result = db.execute("INSERT INTO users(username, hash) VALUES(:username, :hash)",
                            username=request.form.get("username"), hash=generate_password_hash(password))

        if not result:
            return apology("User already exist")

        #  Keep user login
        session["user_id"] = result

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
   # select all names in portfolio
    all_names = db.execute("SELECT symbol FROM portfolio WHERE id = :id", id=session["user_id"])

    if request.method == "GET":
        return render_template("sell.html", name=all_names)
    else:
        stock = lookup(request.form.get("symbol"))
        if not stock:
            return apology("Fails to Select A Stock")

        # Check if the shares is a positive integer
        # check non-numeric
        try:
            shares = float(request.form.get("shares"))
        except ValueError:
            return apology("Share is not a positive integer")

        # check negative
        if shares < 0:
            return apology("Share is not a positive integer")

        # check fraction
        if shares - round(shares) != 0:
            return apology("Share is not a positive integer")

        # Select which stock to sell
        symbol = request.form.get("symbol")
        # print(symbol)

        # check if user could afford the stock
        shares_you_have = db.execute(
            "SELECT shares FROM portfolio WHERE id = :id AND symbol = :symbol", id=session["user_id"], symbol=symbol)

        # check if user could afford the stock
        if not shares_you_have or shares_you_have[0]["shares"] < shares:
            return apology("Shares are not enough")

        # Get time for history
        occrent_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        db.execute("INSERT INTO history (id, symbol, shares, price, transacted) VALUES( :id, :symbol, :shares, :price, :transacted)",
                   id=session["user_id"], symbol=stock["symbol"], price=stock["price"], shares=shares, transacted=occrent_time)

        # sell more of the same stock
        original_shares = db.execute(
            "SELECT shares FROM portfolio WHERE id = :id AND symbol = :symbol", id=session["user_id"], symbol=symbol)

        original_total = db.execute(
            "SELECT total FROM portfolio WHERE id = :id AND symbol = :symbol", id=session["user_id"], symbol=symbol)
        db.execute("UPDATE portfolio SET shares =:share, total= :total WHERE id = :id AND symbol =:symbol",
                   id=session["user_id"], symbol=stock["symbol"], share=original_shares[0]["shares"] - shares, total=-stock["price"] * shares + original_total[0]["total"])

        # Update cash
        db.execute("UPDATE users SET cash = cash + :buy WHERE id = :id",
                    buy=stock['price'] * shares, id=session["user_id"])

        return redirect("/")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
