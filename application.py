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


@app.route("/articles")
def articles():
    """Look up articles for geo"""

    geo = request.args.get("geo")

    if not geo:
        raise RuntimeError("geo not found")

    articles = db.execute("SELECT * FROM parking WHERE key = :k", k=geo)
    # print(articles)

    # session["skey"] = geo

    return jsonify(articles)


@app.route("/search")
def search():
    """Search for places that match query"""

    # session.clear()

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


@app.route("/calculate", methods=["GET", "POST"])
def calculate():
    """Calculate Value"""

    if request.method == "GET":
        print("test")
        return render_template("calculate.html")


    else:

        sekey = request.form["skey"]
        print("kkkkkkkkkkkkkkkkk"+str(sekey))

        # row = db.execute("SELECT * FROM parking WHERE key = :a", a=sekey)
        # print("jhhhhhhhhhh"+row)

        # unitprice = row["Price_per_sqft"]

        # area = row["BldgArea"]

        # # Manhattan setback requirements: avg. 15ft
        # if area == "0" and row["NumFloors"] != 0:
        #     area = (row["SHAPE_Area"] - row["SHAPE_Leng"] * 15 ) * row["NumFloors"]

        # if row["NumFloors"] == 0:
        #     numf = request.form.get("num_f")
        #     area = (row["SHAPE_Area"] - row["SHAPE_Leng"] * 15 ) * numf

        # # Ensure input is positive integer
        # if not request.form.get("pct_a").isdigit() or int(request.form.get("pct_a")) <= 0:
        #     return apology("input must be positive integer", 400)
        # if not request.form.get("pct_b").isdigit() or int(request.form.get("pct_b")) <= 0:
        #     return apology("input must be positive integer", 400)
        # if not request.form.get("pct_c").isdigit() or int(request.form.get("pct_c")) <= 0:
        #     return apology("input must be positive integer", 400)

        # # scroll down menu should be 0-100 for pct_a, 0-remaining for pct_b, 0-remaning for pct_c

        # pcta = request.form.get("pct_a") * 0.01
        # unita = request.form.get("unit_a")
        # pctb = request.form.get("pct_b") * 0.01
        # unitb = request.form.get("unit_b")
        # pctc = request.form.get("pct_c") * 0.01
        # unitc = request.form.get("unit_c")

        # areaa = db.execute("SELECT area FROM unittype WHERE type = :u", u="Studio")
        # areab = db.execute("SELECT area FROM unittype WHERE type = :u", u="One bedroom")
        # areac = db.execute("SELECT area FROM unittype WHERE type = :u", u="Two bedroom")

        # numa = int( (area * pcta) / areaa )
        # numb = int( (area * pctb) / areab )
        # numc = int( (area * pctc) / areac )

        # totalprice = (numa * areaa + numb * areab + numc * areac) * unitprice

        return render_template("calculate.html")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# # listen for errors
# for code in default_exceptions:
#     app.errorhandler(code)(errorhandler)
