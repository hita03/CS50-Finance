import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import sys
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

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

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

infos= {
    "name":None,
    "symbol":None,
    "prices":None
}

@app.route("/")
@login_required
def index():
    '''index = db.execute("SELECT symbol, name, shares, price, total FROM transactions WHERE user_id = :user_id", user_id = session["user_id"])
    cash_query = db.execute("SELECT cash FROM users where id= :id", id= session["user_id"])
    cash= cash_query[0]["cash"]
    return render_template("index.html", index=index, cash=cash)
    '''

    """Show portfolio of stocks"""
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "GET":
        return render_template("buy.html")
    elif request.method == "POST":
        shares = request.form.get("shares")
        if not shares:
            return apology("Invalid shares")
        symbol= request.form.get("symbol").upper()
        if symbol != None:
            stock = lookup(symbol)
            if stock is not None:
                total_price= int(shares)*float(stock["price"])
                cash1= db.execute("SELECT cash from users where id =:id", id= session["user_id"])
                cash = cash1[0]["cash"]
                if total_price> cash:
                    return apology("Can't afford")
                cash= cash - total_price
                db.execute("UPDATE users SET cash=:cash where id=:id", cash=cash, id=session["user_id"])
                print(str(session["user_id"]))
               # print(str(UID))
                flag=4
                db.execute("INSERT INTO shares(UID, symbol, name, shares, price, total, type) VALUES (?,?,?,?,?,?,'Buy')", session["user_id"], stock["symbol"], stock["name"], shares, float(stock["price"]), total_price)
                rows = db.execute("SELECT symbol, name, shares, price, total FROM shares where UID =:UID and type=:types", UID=session["user_id"], types='Buy')
                sym= db.execute("SELECT symbol from cumulative where uid=:uid", uid= session["user_id"])
                print("length of sym: "+ str(len(sym)))
                print(sym)
                if len(sym)==0:
                    db.execute("INSERT INTO cumulative(UID, symbol, name, shares, price, total) VALUES (?,?,?,?,?,?)", session["user_id"], stock["symbol"], stock["name"], shares, float(stock["price"]), total_price)
                else:
                    for i in range(len(sym)):
                        if symbol not in sym[i]["symbol"]:
                            print(str(flag )+ "first val")
                            flag=0
                        else:
                            print(str(flag) + "first(else) val")
                            flag=1
                            break

                    if flag==0:
                        print(str(flag) + "second val")
                        db.execute("INSERT INTO cumulative(UID, symbol, name, shares, price, total) VALUES (?,?,?,?,?,?)", session["user_id"], stock["symbol"], stock["name"], shares, float(stock["price"]), total_price)
                    elif flag==1:
                        print(str(flag) +"third val")
                        shares1 = db.execute("SELECT sum(shares) as s from shares where UID=:UID and symbol=:symbol", UID= session['user_id'], symbol=symbol)
                        db.execute("UPDATE cumulative set shares = :shares where symbol=:symbol and UID=:UID", shares= int(shares1[0]["s"]), symbol=symbol, UID=session["user_id"])
                        db.execute("UPDATE cumulative set total = :total where symbol=:symbol and UID=:UID", total= int(shares)*float(stock["price"]), symbol=symbol, UID=session["user_id"])

                i = len(rows) - 1
                return render_template("bought.html", rows=rows, cash=cash,i=i)
    return apology("Invalid symbol")






@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


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
    if request.method == "GET":
        return render_template("quote.html")
    elif request.method == "POST":
        symbol= request.form.get("symbol")
        if not symbol:
            return apology("No stock symbol given")
        # Store the infos coming from lookup object
        infos = lookup(symbol)
        # Iterate them for rendering
        #for info in infos:
        # If the symbol does not exist in the object
        if symbol != infos["symbol"]:
            return apology("Please use a verified symbol.")
        # If it exists
        else:
            companySymbol = infos["symbol"]
            companyName = infos["name"]
            prices = usd(float(infos["price"]))
            # Render them in quoted.html
            return render_template("quoted.html", companySymbol=companySymbol, companyName=companyName, prices=prices)




@app.route("/register", methods=["GET", "POST"])
def register():
# Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        password= request.form.get("password")
        confirmation= request.form.get("confirmation")
        username=request.form.get("username")
        if not username:
            return apology("must provide username", 403)
        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 403)
        elif not confirmation:
            return apology("must provide confirmation password", 403)
        elif request.form.get("password")!=request.form.get("confirmation"):
            return apology("Password and confirmation password are not same", 403)

        password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        # Insert into database
        db.execute("INSERT INTO users(username, hash) VALUES(:username, :password)", username=username, password= password)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method== "GET":
        options= db.execute("SELECT symbol from cumulative where UID =:UID",UID=session["user_id"])
        return render_template("sell.html", options= options)
    else:
        symbol= request.form.get("symbol")
        shares2= request.form.get("shares")
        if not symbol:
            return apology("No symbol selected.")
        if not shares2:
            return apology("No shares entered.")
        shares1 = db.execute("SELECT sum(shares) as s from shares where UID=:UID and symbol=:symbols", UID= session['user_id'], symbols=symbol)
        shares=int(shares1[0]["s"])
        if int(shares2) > int(shares1[0]["s"]):
            return apology("Can't afford.")
        else:
            stock = lookup(symbol)
            if stock is not None:
                total_price= int(shares2)*float(stock["price"])
                cash1= db.execute("SELECT cash from users where id =:id", id= session["user_id"])
                cash = cash1[0]["cash"]
                cash= cash + total_price
                db.execute("UPDATE users SET cash=:cash where id=:id", cash=cash, id=session["user_id"])
                #print(str(session["user_id"]))
               # print(str(UID))
                db.execute("INSERT INTO shares(UID, symbol, name, shares, price, total, type) VALUES (?,?,?,?,?,?,'Sell')", session["user_id"], stock["symbol"], stock["name"], int(shares2), float(stock["price"]), total_price)
                print("Line 247"+ str(shares))
                shares= shares- int(shares2)
                print("Line 249"+ str(shares))
                db.execute("UPDATE cumulative set shares = :share where symbol=:symbol and UID=:UID", share= shares, symbol=symbol, UID=session["user_id"])
                db.execute("UPDATE cumulative set total = :total where symbol=:symbol and UID=:UID", total= int(shares)*float(stock["price"]), symbol=symbol, UID=session["user_id"])
                rows = db.execute("SELECT symbol, name, shares, price, total FROM cumulative where UID =:UID", UID=session["user_id"])
                return render_template("sold.html", rows=rows, cash=cash)

    return apology("AN ERROR")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
