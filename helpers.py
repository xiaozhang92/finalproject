import csv
import feedparser
import urllib.parse
import urllib.request

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Renders message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



# def lookup(geo):
#     """Look up articles for geo"""

#     # Check cache
#     try:
#         if geo in lookup.cache:
#             return lookup.cache[geo]
#     except AttributeError:
#         lookup.cache = {}

#     # Replace special characters
#     escaped = urllib.parse.quote(geo, safe="")

#     # Get feed from Google
#     feed = feedparser.parse(f"https://news.google.com/news/rss/local/section/geo/{escaped}")

#     # If no items in feed, get feed from Onion
#     if not feed["items"]:
#         feed = feedparser.parse("http://www.theonion.com/feeds/rss")

#     # Cache results
#     lookup.cache[geo] = [{"link": item["link"], "title": item["title"]} for item in feed["items"]]

#     # Return results
#     return lookup.cache[geo]


def usd(value):
    """Formats value as USD."""
    return f"${value:,.2f}"