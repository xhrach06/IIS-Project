from flask import Flask, request, render_template, session, redirect, url_for, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL

# edit user missing
# add device missing html
# logout button missing
# register and profile discrepency (address)
# user devices accessible only through profile

app = Flask(__name__)

app.secret_key = b'7s86sd5fsd567fs5678'

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'iis'
app.config['MYSQL_PASSWORD'] = 'iis'
app.config['MYSQL_DB'] = 'iis'

mysql = MySQL(app)

def dbQueryEscaped(query, data):
    cur = mysql.connection.cursor()
    cur.execute(query, data)
    dbresponse = cur.fetchall()
    cur.close()
    return dbresponse


@app.route("/")
@app.route("/home")
def index():
    return render_template("homepage.html");


@app.route("/login", methods=["GET", "POST"])
def login():
    if "email" in session:
        return redirect(url_for('profile'))
    if request.method == "POST":
            name = request.form["user"]
            passw = request.form["pass"]
            if passw == "123":
                session["username"] = request.form["user"]
                session["userId"] = 123
                return redirect(url_for('profile'))
            else:
                return render_template("login.html")
    return render_template("login.html")


@app.route("/register")
def register():
    if "email" in session:
        return redirect(url_for("profile"))
    return render_template("register.html")


@app.route("/profile")
def profile():
    if "email" in session:
        data = dbQueryEscaped("SELECT first_name,email,last_name FROM user WHERE login=%s", [session["email"]])
        json_data = {"username": data[0][0],
                     "email": data[0][1],
                     "phone": data[0][2],
                     "address": "unknown"}
        return render_template("profile.html", profile_data=json_data)
    return redirect(url_for('login'))


@app.route("/devices")
def devices():
    return render_template("devices.html")


@app.route("/systems")
def systems():
    return render_template("systems.html")


@app.route("/my-device")
def my_device():
    return render_template("my-device.html")


@app.route("/edit-device")
def edit_device():
    return render_template("edit-device.html")


@app.route("/edit-system")
def edit_system():
    return render_template("system-detail.html")


@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))


# ----- API -----

@app.route("/api/register", methods=["POST"]) # TODO: do more duplicate checks
def api_reg():
    form_data = request.get_json() #email = LOGIN
    #check for duplicates
    cur = mysql.connection.cursor()
    cur.execute("SELECT login FROM user WHERE login=%s;", [form_data["email"]])
    response = cur.fetchall()
    if (len(response) > 0):
        cur.close()
        return {"error": True, "message": "Email already in use."}
    
    #insert new user into DB
    pass_hash = generate_password_hash(form_data["password"], salt_length=109)
    try: # try adding user to DB
        cur.execute("INSERT INTO user VALUES (%s,%s,%s,%s,%s,0)",
                   [form_data["email"], form_data["name"], form_data["surname"],
                    pass_hash, form_data["email"]])
        mysql.connection.commit()
        cur.close()
    except Exception as e: # check for wrong format email
        error_code = e.args[0] if e.args else None 
        if (error_code == 3819):
            return {"error": True, "message": "Email is in wrong format."}
        else:
            return {"error": True, "message": "Unknown error."}
    session["email"] = form_data["email"]
    return {"error": False}


@app.route("/api/login", methods=["POST"])
def api_login():
    form_data = request.get_json()
    response = dbQueryEscaped("SELECT login, password FROM user WHERE login=%s;", [form_data["email"]])
    if (len(response) > 0):
        if (check_password_hash(response[0][1], form_data["password"])):
            session["email"] = form_data["email"]
            return {"error": False}
    return {"error": True, "message": "Email or password is wrong."}



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)