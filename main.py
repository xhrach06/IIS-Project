from flask import Flask, request, render_template, session, redirect, url_for, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL

# TODO: sharing systems in DB
# TODO: admin page
# TODO: broker
# TODO: add delete device, system
# TODO: sesion timeout


app = Flask(__name__)

app.secret_key = b'7s86sd5fsd567fs5678'

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'iis'
app.config['MYSQL_PASSWORD'] = 'iis'
app.config['MYSQL_DB'] = 'iis'

mysql = MySQL(app)

print(mysql)

def dbQueryEscaped(query, data, cur):
    cur.execute(query, data)
    dbresponse = cur.fetchall()
    cur.close()
    return dbresponse

def dbQuery(query, cur):
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
        cur = mysql.connection.cursor()
        response = dbQuery("""SELECT systems.system_id, name, dev_count, first_name, last_name, created_date FROM systems
            LEFT JOIN (SELECT system_id, COUNT(system_id) as dev_count FROM device_systems GROUP BY system_id) AS device_count
            ON systems.system_id=device_count.system_id INNER JOIN user ON systems.user_id=user.user_id;""", cur)
        return render_template("not-logged.html", systems=response);


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
        cur = mysql.connection.cursor()
        response = dbQueryEscaped("SELECT first_name,last_name,email,registration_date FROM user WHERE user_id=%s;", [session["user_id"]], cur)
        return render_template("profile.html", profile=response)
    return redirect(url_for('login'))


@app.route("/edit-profile")
def edit_profile():
    if "user_id" in session:
        cur = mysql.connection.cursor()
        response = dbQueryEscaped("SELECT first_name,last_name,email FROM user WHERE user_id=%s;", [session["user_id"]], cur)
        return render_template("edit-profile.html", profile=response)
    return redirect(url_for('login'))


@app.route("/delete-profile")
def delete_profile():
    if "user_id" in session:
        return render_template("delete-profile.html")
    return redirect(url_for('login'))


@app.route("/change-password")
def change_password():
    if "user_id" in session:
        return render_template("change-password.html")
    return redirect(url_for('login'))


@app.route("/manage-devices")
def manage_devices():
    if "user_id" in session:
        cur = mysql.connection.cursor()
        response = dbQueryEscaped("""SELECT device.name, description, parameter.name, 
                                    kpi_on_off, ok_if, kpi_treshold, current_value, device.device_id FROM device, parameter 
                                  WHERE user_id=%s AND device.device_id=parameter.device_id;""", [session["user_id"]], cur)
        data = []
        for r in response:
            dev = []
            dev.append(r[0])
            dev.append(r[1])
            dev.append(r[2])
            if (r[3]):
                if ((r[4]==0 and r[5]>r[6]) or (r[4]==1 and r[5]<r[6])):
                    dev.append(1)
                else:
                    dev.append(0)
            else:
                dev.append(-1)
            dev.append(r[7])
            dev.append(r[6])
            data.append(dev)
        return render_template("manage-devices.html", devices=data)
    return redirect(url_for('index'))


@app.route("/systems")
def systems():
    if "user_id" in session:
        cur = mysql.connection.cursor()
        response = dbQuery("""SELECT systems.system_id, name, dev_count, first_name, last_name, created_date FROM systems
            LEFT JOIN (SELECT system_id, COUNT(system_id) as dev_count FROM device_systems GROUP BY system_id) AS device_count
            ON systems.system_id=device_count.system_id INNER JOIN user ON systems.user_id=user.user_id;""", cur)
        return render_template("show-all-systems.html", systems=response)
    return redirect(url_for('index'))


@app.route("/my-systems")
def my_systems():
    if "user_id" in session:
        cur = mysql.connection.cursor()
        response = dbQueryEscaped("""SELECT systems.system_id, name, dev_count, first_name, last_name, created_date FROM systems
            LEFT JOIN (SELECT system_id, COUNT(system_id) as dev_count FROM device_systems GROUP BY system_id) AS device_count
            ON systems.system_id=device_count.system_id INNER JOIN user ON systems.user_id=user.user_id WHERE systems.user_id=%s;""", [session["user_id"]], cur)
        data = []
        for system in response:
            data_one = []
            data_one.append(system[0])
            data_one.append(system[1])
            data_one.append(system[2])
            data_one.append(system[3])
            data_one.append(system[4])
            data_one.append(system[5])
            cur = mysql.connection.cursor()
            res = dbQueryEscaped("""SELECT kpi_on_off, ok_if, kpi_treshold, current_value FROM parameter p, device d, device_systems s 
                                    WHERE d.device_id=s.device_id AND p.device_id=d.device_id AND s.system_id=%s;""", [system[0]], cur)
            print(res)
            is_ok = 1
            for param in res:
                if (param[0] == 1):
                    if ((param[1] == 1 and param[2]<param[3]) or (param[1] == 0 and param[2]>param[3])):
                        is_ok = is_ok
                    else:
                        is_ok = 0
            data_one.append(is_ok)
            data.append(data_one)
        print(data)
        #print(response)
        return render_template("show-my-systems.html", systems=data)
    return redirect(url_for('index'))


@app.route("/add-system")
def add_system():
    if "user_id" in session:
        cur = mysql.connection.cursor()
        response = dbQueryEscaped("SELECT device_id, name, description FROM device WHERE user_id=%s;", [session["user_id"]], cur)
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
        device_id = request.args.get("device_id", default=None, type=int)
        if (device_id != None):
            cur = mysql.connection.cursor()
            response = dbQueryEscaped("SELECT user_id FROM device WHERE device_id=%s;", [device_id], cur)
            if (len(response) > 0 and response[0][0] == session["user_id"]):
                cur = mysql.connection.cursor()
                response = dbQueryEscaped("""SELECT d.name, d.description, p.name, p.max_value, p.min_value, p.kpi_on_off, p.ok_if,
                                 p.kpi_treshold,d.device_id,p.param_id FROM
                                device d, parameter p WHERE d.device_id=p.device_id AND d.device_id=%s""", [device_id], cur)
                kpi_data = []
                if (response[0][5]):
                    kpi_data.append("KPI ON")
                else:
                    kpi_data.append("KPI OFF")
                if (response[0][6]):
                    kpi_data.append("Higher")
                else:
                    kpi_data.append("Lower")
                return render_template("edit-device.html", device=response, kpi=kpi_data)
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
            cur = mysql.connection.cursor()
            response = dbQueryEscaped("SELECT user_id FROM systems WHERE system_id=%s;", [sys_id], cur)
            if (len(response) > 0 and response[0][0] == session["user_id"]):
                cur = mysql.connection.cursor()
                response = dbQueryEscaped("""SELECT device.name, description, parameter.name, kpi_on_off, ok_if, kpi_treshold, current_value, device.device_id
                                 FROM device, parameter, device_systems 
                                  WHERE device.device_id=parameter.device_id AND device_systems.system_id=%s 
                                  AND device.device_id=device_systems.device_id;""", [sys_id], cur)
                print(response)
                data = []
                for r in response:
                    dev = []
                    dev.append(r[0])
                    dev.append(r[1])
                    dev.append(r[2])
                    if (r[3]):
                        if ((r[4]==0 and r[5]>r[6]) or (r[4]==1 and r[5]<r[6])):
                            dev.append(1)
                        else:
                            dev.append(0)
                    else:
                        dev.append(-1)
                    dev.append(r[7])
                    dev.append(r[6])
                    data.append(dev)
                print(data)
                return render_template("system-show-devices.html", devices=data)
    return redirect(url_for('index'))


@app.route("/manage-system")
def manage_system():
    if "user_id" in session:
        sys_id = request.args.get("sys_id", default=None, type=int)
        if (sys_id != None):
            cur = mysql.connection.cursor()
            response = dbQueryEscaped("SELECT user_id FROM systems WHERE system_id=%s;", [sys_id], cur)
            if (len(response) > 0 and response[0][0] == session["user_id"]):
                cur = mysql.connection.cursor()
                response = dbQueryEscaped("SELECT device_id, name, description FROM device WHERE user_id=%s;", [session["user_id"]], cur)
                cur = mysql.connection.cursor()
                response2 = dbQueryEscaped("""SELECT device.device_id, name, description FROM device, device_systems 
                                            WHERE device.device_id=device_systems.device_id AND device_systems.system_id=%s;""", [sys_id], cur)
                cur = mysql.connection.cursor()
                response3 = dbQueryEscaped("SELECT name, description, system_id FROM systems WHERE system_id=%s;", [sys_id], cur)
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
    cur = mysql.connection.cursor()
    response = dbQueryEscaped("SELECT user_id, password FROM user WHERE email=%s;", [form_data["email"]], cur)
    if (len(response) > 0):
        if (check_password_hash(response[0][1], form_data["password"])):
            session["user_id"] = response[0][0]
            return {"error": False}
    return {"error": True, "message": "Email or password is wrong."}


@app.route("/api/change-password", methods=["POST"])
def api_change_password():
    form_data = request.get_json()
    cur = mysql.connection.cursor()
    response = dbQueryEscaped("SELECT password FROM user WHERE user_id=%s;", [session["user_id"]], cur)
    print(response)
    print(request.get_json())
    if (len(response) > 0):
        if (check_password_hash(response[0][0], form_data["password"])):
            try:
                cur = mysql.connection.cursor()
                new_hash = generate_password_hash(form_data["new_password"], salt_length=109)
                cur.execute("UPDATE user SET password=%s WHERE user_id=%s;", [new_hash, session["user_id"]])
                mysql.connection.commit()
                last_id = cur.lastrowid
                cur.close()
                return {"error": False}
            except Exception as e:
                error_code = e.args[0] if e.args else None
                print(e)
                print(error_code) 
                return {"error": True, "message": "Unknown error."}
    return {"error": True, "message": "Password is wrong."}


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
    response = dbQueryEscaped("SELECT user_id FROM systems WHERE system_id=%s", [form_data["system_id"]], cur)
    if (len(response)>0 and response[0][0] != session["user_id"]):
        return {"error": True, "message": "Unauthorized."}
    
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


@app.route("/api/edit-device", methods=["POST"])
def api_edit_device():
    form_data = request.get_json()
    cur = mysql.connection.cursor()
    response = dbQueryEscaped("SELECT user_id FROM device WHERE device_id=%s", [form_data["device_id"]], cur)
    if (len(response)>0 and response[0][0] != session["user_id"]):
        return {"error": True, "message": "Unauthorized."}

    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE device SET name=%s, description=%s WHERE device_id=%s;",
                   [form_data["name"], form_data["description"], form_data["device_id"]])
        cur.execute("""UPDATE parameter SET name=%s, max_value=%s, min_value=%s, kpi_on_off=%s, ok_if=%s, kpi_treshold=%s WHERE param_id=%s;""",
                   [form_data["param_name"], int(form_data["max_value"]), int(form_data["min_value"]), int(form_data["kpi"] == "KPI ON"),
                    int(form_data["ok_if"]=="Higher"), float(form_data["treshold"]), form_data["param_id"]])
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        error_code = e.args[0] if e.args else None
        print(e)
        cur.close()
        return {"error": True, "message": "Unknown error."}
    return {"error": False}


@app.route("/api/edit-profile", methods=["POST"])
def api_edit_profile():
    form_data = request.get_json()
    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE user SET first_name=%s, last_name=%s, email=%s WHERE user_id=%s;",
                   [form_data["first_name"], form_data["last_name"], form_data["email"], session["user_id"]])
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        error_code = e.args[0] if e.args else None
        print(e)
        cur.close()
        if (error_code == 3819):
            return {"error": True, "message": "Email is in wrong format."}
        elif (error_code == 1062):
            return {"error": True, "message": "Email already in use."}
        else:
            return {"error": True, "message": "Unknown error."}
    return {"error": False}


@app.route("/api/delete-profile", methods=["POST"])
def api_delete_profile():
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM user WHERE user_id=%s;", [session["user_id"]])
        mysql.connection.commit()
        cur.close()
        session.pop('user_id', None)
    except Exception as e:
        error_code = e.args[0] if e.args else None
        print(e)
        cur.close()
        return {"error": True, "message": "Unknown error."}
    return {"error": False}


@app.route("/api/update", methods=["POST"])
def api_update():
    form_data = request.get_json()
    print(form_data)
    cur = mysql.connection.cursor()
    response = dbQueryEscaped("SELECT user_id, password FROM user WHERE email=%s;", [form_data["email"]], cur)
    if (len(response) > 0):
        if (check_password_hash(response[0][1], form_data["password"])):
            user_id = response[0][0]
            cur = mysql.connection.cursor()
            response = dbQueryEscaped("SELECT user_id, device_id FROM device WHERE device_id=%s;", [form_data["device_id"]], cur)
            cur = mysql.connection.cursor()
            param_res = dbQueryEscaped("SELECT min_value, max_value FROM device d,parameter p WHERE d.device_id=%s AND d.device_id=p.device_id;", [form_data["device_id"]], cur)
            print(user_id)
            if (len(response) > 0):
                if (response[0][0] == user_id):
                    value = form_data["value"]
                    if (value < param_res[0][0]):
                        value = param_res[0][0]
                    if (value > param_res[0][1]):
                        value = param_res[0][1]
                    cur = mysql.connection.cursor()
                    try:
                        cur.execute("UPDATE parameter SET current_value=%s WHERE device_id=%s;",[value,form_data["device_id"]])
                        mysql.connection.commit()
                        cur.close()
                    except Exception as e:
                        error_code = e.args[0] if e.args else None
                        print(e)
                        cur.close()
                        return {"error": True, "message": "Unknown error."}
                    return {"error": False}
            return {"error": True, "message": "Device doesn't exist or isn't yours."}
    return {"error": True, "message": "Email or password is wrong."}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)