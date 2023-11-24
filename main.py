from flask import Flask, request, render_template, session, redirect, url_for, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL

# ask what html is my-systems/manage system
# when adding new device, can only be one parameter


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

def dbQuery(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    dbresponse = cur.fetchall()
    cur.close()
    return dbresponse


@app.route("/")
@app.route("/home")
def index():
    if "user_id" in session:
        return render_template("logged-home.html");
    else:
        return render_template("not-logged.html");

@app.route("/login")
def login():
    if "user_id" in session:
        return redirect(url_for('index'))
    else:
        return render_template("login.html")


@app.route("/register")
def register():
    if "user_id" in session:
        return redirect(url_for("profile"))
    return render_template("register.html")


@app.route("/profile")
def profile():
    if "user_id" in session:
        data = dbQueryEscaped("SELECT first_name,email,last_name FROM user WHERE login=%s;", [session["email"]])
        json_data = {"username": data[0][0],
                     "email": data[0][1],
                     "phone": data[0][2],
                     "address": "unknown"}
        return render_template("profile.html", profile_data=json_data)
    return redirect(url_for('login'))


@app.route("/manage-devices")
def manage_devices():
    if "user_id" in session:
        response = dbQueryEscaped("""SELECT device.name, description, parameter.name FROM device, parameter 
                                  WHERE user_id=%s AND device.device_id=parameter.device_id;""", [session["user_id"]])
        print(response)
        return render_template("manage-devices.html", devices=response)
    return redirect(url_for('index'))


@app.route("/systems")
def systems():
    if "user_id" in session:
        return render_template("show-all-systems.html")
    return redirect(url_for('index'))


@app.route("/my-systems")
def my_systems():
    if "user_id" in session:
        response = dbQueryEscaped("""SELECT systems.system_id, name, dev_count, first_name, last_name FROM systems
            LEFT JOIN (SELECT system_id, COUNT(system_id) as dev_count FROM device_systems GROUP BY system_id) AS device_count
            ON systems.system_id=device_count.system_id INNER JOIN user ON systems.user_id=user.user_id WHERE systems.user_id=%s;""", [session["user_id"]])
        print(response)
        return render_template("show-my-systems.html", systems=response)
    return redirect(url_for('index'))


@app.route("/add-system")
def add_system():
    if "user_id" in session:
        response = dbQueryEscaped("SELECT device_id, name, description FROM device WHERE user_id=%s;", [session["user_id"]])
        return render_template("add-system.html", devices=response)
    return redirect(url_for('index'))


@app.route("/my-device")
def my_device():
    if "user_id" in session:
        return render_template("my-device.html")
    return redirect(url_for('index'))


@app.route("/edit-device")
def edit_device():
    if "user_id" in session:
        return render_template("edit-device.html")
    return redirect(url_for('index'))


@app.route("/add-device")
def add_device():
    if "user_id" in session:
        return render_template("add-device.html")
    return redirect(url_for('index'))


@app.route("/show-system")
def show_system():
    if "user_id" in session:
        sys_id = request.args.get("sys_id", default=None, type=int)
        if (sys_id != None):
            response = dbQueryEscaped("SELECT user_id FROM systems WHERE system_id=%s;", [sys_id])
            if (len(response) > 0 and response[0][0] == session["user_id"]):
                response = dbQueryEscaped("""SELECT device.name, description, parameter.name FROM device, parameter, device_systems 
                                  WHERE device.device_id=parameter.device_id AND device_systems.system_id=%s 
                                  AND device.device_id=device_systems.device_id;""", [sys_id])
                return render_template("system-show-devices.html", devices=response)
    return redirect(url_for('index'))


@app.route("/manage-system")
def manage_system():
    if "user_id" in session:
        sys_id = request.args.get("sys_id", default=None, type=int)
        if (sys_id != None):
            response = dbQueryEscaped("SELECT user_id FROM systems WHERE system_id=%s;", [sys_id])
            if (len(response) > 0 and response[0][0] == session["user_id"]):
                response = dbQueryEscaped("SELECT device_id, name, description FROM device WHERE user_id=%s;", [session["user_id"]])
                response2 = dbQueryEscaped("""SELECT device.device_id, name, description FROM device, device_systems 
                                            WHERE device.device_id=device_systems.device_id AND device_systems.system_id=%s;""", [sys_id])
                response3 = dbQueryEscaped("SELECT name, description, system_id FROM systems WHERE system_id=%s;", [sys_id])
                print(response)
                print(response2)
                return render_template("edit-system.html", devices=response, sys_devices=response2, system=response3)
    return redirect(url_for('index'))


@app.route("/sharing-options")
def sharing_options():
    if "user_id" in session:
        return render_template("sharing-options.html")
    return redirect(url_for('index'))


@app.route("/logout")
def logout():
    if "user_id" in session:
        session.pop('user_id', None)
    return redirect(url_for('index'))


# ----- API -----

@app.route("/api/register", methods=["POST"])
def api_reg():
    last_id = None
    form_data = request.get_json()
    cur = mysql.connection.cursor()
    #insert new user into DB
    pass_hash = generate_password_hash(form_data["password"], salt_length=109)
    try: # try adding user to DB
        cur.execute("INSERT INTO user (first_name, last_name, password, email) VALUES (%s,%s,%s,%s);",
                   [form_data["name"], form_data["surname"], pass_hash, form_data["email"]])
        mysql.connection.commit()
        last_id = cur.lastrowid
        cur.close()
    except Exception as e: # check for wrong format email
        error_code = e.args[0] if e.args else None
        print(error_code) 
        if (error_code == 3819):
            return {"error": True, "message": "Email is in wrong format."}
        elif (error_code == 1062):
            return {"error": True, "message": "Email already in use."}
        else:
            return {"error": True, "message": "Unknown error."}
    session["user_id"] = last_id
    return {"error": False}


@app.route("/api/login", methods=["POST"])
def api_login():
    form_data = request.get_json()
    response = dbQueryEscaped("SELECT user_id, password FROM user WHERE email=%s;", [form_data["email"]])
    if (len(response) > 0):
        if (check_password_hash(response[0][1], form_data["password"])):
            session["user_id"] = response[0][0]
            return {"error": False}
    return {"error": True, "message": "Email or password is wrong."}


@app.route("/api/add-device", methods=["POST"])
def api_add_device():
    form_data = request.get_json()
    cur = mysql.connection.cursor()
    try: # try adding device to DB
        cur.execute("INSERT INTO device (name, description, user_id) VALUES (%s,%s,%s);",
                   [form_data["name"], form_data["description"], session["user_id"]])
        #mysql.connection.commit()
        last_id = cur.lastrowid
        cur.execute("INSERT INTO parameter (name, max_value, min_value, kpi_on_off, ok_if, kpi_treshold, device_id) VALUES (%s,%s,%s,%s,%s,%s,%s);",
                   [form_data["param_name"], int(form_data["max_value"]), int(form_data["min_value"]), int(form_data["kpi"] == "KPI ON"),
                    int(form_data["ok_if"]=="Higher"), float(form_data["treshold"]), last_id])
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        error_code = e.args[0] if e.args else None
        cur.close()
        return {"error": True, "message": "Unknown error."}
    print(form_data)
    return {"error": False}


@app.route("/api/add-system", methods=["POST"])
def api_add_system():
    form_data = request.get_json()
    cur = mysql.connection.cursor()
    try: # try adding system to DB
        cur.execute("INSERT INTO systems (name, description, user_id) VALUES (%s,%s,%s);",
                   [form_data["name"], form_data["description"], session["user_id"]])
        #mysql.connection.commit()
        last_id = cur.lastrowid
        for device_id in form_data["device_ids"]:
            cur.execute("INSERT INTO device_systems (system_id, device_id) VALUES (%s,%s);",
                    [last_id, int(device_id)])
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        error_code = e.args[0] if e.args else None
        cur.close()
        return {"error": True, "message": "Unknown error."}
    print(form_data)
    return {"error": False}


@app.route("/api/edit-system", methods=["POST"])
def api_edit_system():
    form_data = request.get_json()
    cur = mysql.connection.cursor()
    try: # try adding system to DB
        cur.execute("UPDATE systems SET name=%s, description=%s WHERE system_id=%s;",
                   [form_data["name"], form_data["description"], form_data["system_id"]])
        #mysql.connection.commit()
        cur.execute("DELETE FROM device_systems WHERE system_id=%s;", [form_data["system_id"]])
        for device_id in form_data["device_ids"]:
            cur.execute("INSERT INTO device_systems (system_id, device_id) VALUES (%s,%s);",
                    [form_data["system_id"], int(device_id)])
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        error_code = e.args[0] if e.args else None
        print(e)
        cur.close()
        return {"error": True, "message": "Unknown error."}
    print(form_data)
    return {"error": False}



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)