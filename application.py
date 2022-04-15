from functools import wraps
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from cs50 import SQL 
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash
from tempfile import mkdtemp

# Configure aplication
app = Flask(__name__)

# Set auto reloading
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SECRET_KEY"] = "OCBsd3hb6DOIUDIWUB976Db8diwvd"

# Prevent data from being cached for long
@app.after_request
def add_header(response):
    response.cache_control.max_age = 1 #1200
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///food.db")

# Initialize a list of possible ingredients to loop over
INGREDIENTS = [
    'baking powder', 'beans', 'beef', 'butter', 'carrot', 'cheese', 'chicken', 
    'cream', 'eggplant', 'eggs', 'garlic', 'flour', 'mayonnaise', 'milk', 
    'mushrooms', 'olive oil', 'onion', 'pasta', 'pork', 'potato', 'rice', 
    'sugar', 'tomato', 'zucchini']


def login_required(f):
    """  Decorate routes to require login.  """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def index(): 

    times = db.execute("""SELECT * FROM dishes 
        JOIN time ON dishes.id = time.dish_id
        WHERE user=? LIMIT 30""", session["username"])
    data = db.execute("""SELECT * FROM dishes
        JOIN ingredients ON dishes.id = ingredients.dish_id
        JOIN recipe ON dishes.id = recipe.dish_id
        WHERE user=? LIMIT 30""", session["username"])

    return render_template("index.html", data=data, times=times)


@app.route("/add", methods=["POST", "GET"])
@login_required
def add():
    """Add dish to database"""
    if request.method == "POST":
        
        # Check if dish name already exists for user
        dish_name_existing = db.execute("SELECT * FROM dishes WHERE name=? AND user=?", request.form.get("dish_name"), session["username"])
        if dish_name_existing:
            flash("You already have that dish in database")
            return render_template("add.html")
        # Insert form data into apropriate tables
        db.execute("INSERT INTO dishes (name, user) VALUES (?,?)", request.form.get("dish_name"), session["username"])
        # Get id used for the dish
        dish_id = db.execute("SELECT id FROM dishes WHERE name=? AND user=?", request.form.get("dish_name"), session["username"])[0]["id"]
        
        # Insert data into time talble
        times = request.form.getlist("eating_time")
        db.execute("INSERT INTO time (dish_id) VALUES (?)", dish_id)  # Create row for new dish
        for time in times:
            db.execute("UPDATE time SET ?=1 WHERE dish_id=?", time, dish_id)  # Update time of eating in new row for every checkbox checked

        # Insert data into ingredients table
        ingrs = request.form.getlist("ingredient")
        db.execute("INSERT INTO ingredients (dish_id) VALUES (?)", dish_id) # Create row for new dish
        for item in ingrs:
            db.execute("UPDATE ingredients SET ?=1 WHERE dish_id=?", item, dish_id) # Update ingredients needed for every checkbox checked

        # Insert data into recipe table
        recipe = request.form.get("recipe")
        db.execute("INSERT INTO recipe (dish_id, recipe) VALUES (?,?)", dish_id, recipe)

        return redirect("/")

    else:
        ingr = INGREDIENTS.copy()
        return render_template("add.html", ingr=ingr)


@app.route("/search", methods=["POST", "GET"])
@login_required
def search():  
    if request.method == "POST":
        # Prepare list for dishes to put out
        dishes_avilable=[]

        # Check if user searched by name, if yes query database
        name = request.form.get("dish_name")
        if name == "":
            dishes = db.execute("""SELECT * FROM dishes
                                JOIN ingredients ON dishes.id = ingredients.dish_id
                                JOIN time ON dishes.id = time.dish_id
                                WHERE user=? LIMIT 30""", session["username"])
        else:
            dishes = db.execute("""SELECT * FROM dishes 
                                JOIN ingredients ON dishes.id = ingredients.dish_id
                                JOIN time ON dishes.id = time.dish_id 
                                WHERE name LIKE ? AND user=?""", name, session["username"])

        # Check for checked(checkbox) time
        time = request.form.get("eating_time")
        if time:
            for dish in dishes:
                if dish[time] == 1:
                    dishes_avilable.append(dish)

        # Check for ingredients marked as avilable and create a list of unavilable ingredients, to eliminate dishes containing them
        ingredients_avilable = request.form.getlist("ingredient")
        if len(ingredients_avilable) > 0:
            ingredients_unavilable = INGREDIENTS.copy()
            for ingredient in ingredients_avilable:
                    ingredients_unavilable.remove(ingredient)     
            
            # Loop over the dishes and informations about necessary ingredient, add dishes where all necessary ingredients are avilable to dishes_avilable list
            for dish in dishes:
                # Variable to check if a dish had an unavilable ingredient
                check = True
                for info in dish:
                    if dish[info] == 1:
                        if info in ingredients_unavilable:
                            check = False
                            continue
                if check:
                    dishes_avilable.append(dish)
        

        if name == "" and not time and len(ingredients_avilable) == 0:
            return render_template("search_result.html", data=dishes)
        elif len(dishes_avilable) == 0:
            if name != "":
                return render_template("search_result.html", data=dishes)
            else:
                return render_template("search_result.html", data="List empty")
        
        return render_template("search_result.html", data=dishes_avilable)



    else:
        ingr = INGREDIENTS.copy()
        return render_template("search.html", ingr=ingr)


@app.route("/register", methods=["POST", "GET"])
def register():
    # Register user
    if request.method == "POST":
        # Check if username and password were submitted
        if not request.form.get("username"):
            flash("Login required")
            return render_template("register.html")

        # Check if username already taken
        existing = db.execute("SELECT username FROM users WHERE username=?", request.form.get("username"))
        if len(existing) > 0:
            flash("Username taken")
            return render_template("register.html")

        # Check if password submited
        if not request.form.get("password"):
           flash("Password required")
           return render_template("register.html")

        # Check if password repeated correctly   
        if not request.form.get("password_repeat") or request.form.get("password_repeat") != request.form.get("password"):
            flash("Repeat password correctly")
            return render_template("register.html")

        # Register user
        db.execute("INSERT INTO users (username, hash) VALUES (?,?)", request.form.get("username"), generate_password_hash(request.form.get("password")))
        
        # Save user as logged in
        session["username"] = request.form.get("username")

        return redirect("/")
        

    else:
        if session.get("username") is None:
            return render_template("register.html")
        else:
            return render_template("already_logged.html")



@app.route("/login", methods=["POST", "GET"])
def login():
    """ log user in """
    if request.method == "POST":
        # Check if username and password were submitted
        if not request.form.get("username"):
            flash("Login required")
            return render_template("login.html")

        if not request.form.get("password"):
           flash("Password required")
           return render_template("login.html")
        
        # Query database for provided username
        rows = db.execute("SELECT * FROM users WHERE username=?", request.form.get("username"))

        # Check if username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):  
            flash("password incorrect")
            return render_template("login.html")
        
        # Save logged user username
        session["username"] = rows[0]["username"]

        # redirect user to homepage
        return redirect("/")

    else:
        if session.get("username") is None:
            return render_template("login.html")
        else:
            return render_template("already_logged.html")

@app.route("/logout", methods=["POST", "GET"])
def logout():
    """Log user out"""
    if request.method == "POST":
         # Forget current user
        session.clear()
        session.pop("username", None)

        #redirect to login
        return redirect("/login")

    else:
        # If no user redirect to login
        if session.get("username") is None: 
            flash("Not logged in")
            return redirect("/login")
        else:
            # If user is logged in allow logout 
            return render_template("logout.html")

@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now handling non-HTTP exceptions only
    return render_template("apology.html", e=e), 500

if __name__=="__main__":
    app.run(debug=True)