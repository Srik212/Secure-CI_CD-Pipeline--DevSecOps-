from flask import Flask, request, session, redirect, url_for, render_template
import os
from dotenv import load_dotenv
from db import get_connection

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-hardcoded-secret")  # [VULN] Hardcoded fallback secret
app.debug = True  # [VULN] DEBUG=True exposes stack traces


# ─── LOGIN 

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_connection()
        cur = conn.cursor()
        # [VULN] SQL Injection — raw string formatting, no parameterization
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cur.execute(query)
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[3]
            if user[3] == "admin":
                return redirect(url_for("admin"))
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials"
    return render_template("login.html", error=error)


# ─── LOGOUT 

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ─── USER DASHBOARD 

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM inventory")
    items = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("dashboard.html", items=items, username=session["username"])


# ─── SEARCH 

@app.route("/search")
def search():
    if "user_id" not in session:
        return redirect(url_for("login"))
    q = request.args.get("q", "")
    conn = get_connection()
    cur = conn.cursor()
    # [VULN] SQL Injection + Reflected XSS — query param injected into SQL and reflected in HTML
    query = f"SELECT * FROM inventory WHERE name LIKE '%{q}%'"
    cur.execute(query)
    items = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("search.html", items=items, query=q)


# ─── ITEM DETAIL 

@app.route("/item/<item_id>")
def item_detail(item_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_connection()
    cur = conn.cursor()
    # [VULN] SQL Injection + IDOR — no ownership check, raw item_id in query
    query = f"SELECT * FROM inventory WHERE id={item_id}"
    cur.execute(query)
    item = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("item.html", item=item)


# ─── ADMIN DASHBOARD 

@app.route("/admin")
def admin():
    # [VULN] Broken Access Control — no role check, any logged-in user can access
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM inventory")
    items = cur.fetchall()
    cur.execute("SELECT id, username, role, email FROM users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("admin.html", items=items, users=users)


@app.route("/admin/add-item", methods=["POST"])
def add_item():
    if "user_id" not in session:
        return redirect(url_for("login"))
    name = request.form["name"]
    description = request.form["description"]
    quantity = request.form["quantity"]
    price = request.form["price"]
    conn = get_connection()
    cur = conn.cursor()
    # [VULN] Stored XSS — name and description stored raw, rendered with |safe in templates
    cur.execute(
        "INSERT INTO inventory (name, description, quantity, price) VALUES (%s, %s, %s, %s)",
        (name, description, quantity, price)
    )
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("admin"))


@app.route("/admin/delete-item/<item_id>", methods=["POST"])
def delete_item(item_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM inventory WHERE id={item_id}")  # [VULN] SQLi
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("admin"))


# ─── DEBUG ROUTE 

@app.route("/debug")
def debug():
    # [VULN] Sensitive Data Exposure — dumps all environment variables
    env_vars = {key: val for key, val in os.environ.items()}
    return {"env": env_vars, "secret_key": app.secret_key, "debug": app.debug}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
