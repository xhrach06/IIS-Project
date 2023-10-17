from flask import Flask, request, render_template, session, redirect, url_for, abort
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = b'7s86sd5fsd567fs5678'

@app.route("/")
@app.route("/home")
def index():
    if "username" in session:
        return render_template("index.html", loggedIn=True)
    else:
        return render_template("index.html", loggedIn=False)


@app.route("/authorize", methods=["GET", "POST"])
def auth():
    if "username" in session:
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


@app.route("/profile")
def profile():
    if "username" in session:
        username = session["username"]
        userId = session["userId"]
        return render_template("profile.html", username=username, userId=userId)
    return redirect(url_for('auth'))


@app.route("/logout")
def logout():
    userId = session["username"]
    userId = session["userId"]
    session.pop('username', None)
    session.pop('userId', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)