import os
import sqlite3
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
DB_PATH = os.environ.get("DATABASE_PATH", "free_cp.db")
ADMIN_G = os.environ.get("ADMIN_G", "")
ADMIN_P_HASH = os.environ.get("ADMIN_P_HASH")
ADMIN_P = os.environ.get("ADMIN_P", "")

PRIZES = ["10 CP", "20 CP", "30 CP", "50 CP", "100 CP", "دوباره تلاش کن", "25 CP", "75 CP"]

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS spins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                g_name TEXT NOT NULL,
                p_name TEXT NOT NULL,
                spun_at TEXT NOT NULL,
                prize TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_names_time ON spins(g_name, p_name, spun_at)")

def admin_password_ok(candidate):
    # Prefer a hashed password in production. ADMIN_P is provided only for easy first setup.
    if ADMIN_P_HASH:
        from werkzeug.security import check_password_hash
        return check_password_hash(ADMIN_P_HASH, candidate)
    return secrets.compare_digest(candidate, ADMIN_P)

def admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapped

@app.route("/")
def home():
    return render_template("index.html")

@app.post("/spin")
def spin():
    g_name = request.form.get("g_name", "").strip()
    p_name = request.form.get("p_name", "").strip()
    if not g_name or not p_name:
        return jsonify(ok=False, message="لطفاً هر دو فیلد G و P را کامل کنید."), 400
    if len(g_name) > 60 or len(p_name) > 60:
        return jsonify(ok=False, message="هر ورودی حداکثر ۶۰ نویسه باشد."), 400

    now = datetime.now(timezone.utc)
    with db() as conn:
        last = conn.execute(
            "SELECT spun_at FROM spins WHERE lower(g_name)=lower(?) AND lower(p_name)=lower(?) ORDER BY id DESC LIMIT 1",
            (g_name, p_name)
        ).fetchone()
        if last:
            last_time = datetime.fromisoformat(last["spun_at"])
            available_at = last_time + timedelta(hours=24)
            if now < available_at:
                remaining = int((available_at - now).total_seconds())
                hours, rem = divmod(remaining, 3600)
                minutes = rem // 60
                return jsonify(ok=False, message=f"این مشخصات قبلاً چرخانده‌اند. {hours} ساعت و {minutes} دقیقه دیگر دوباره تلاش کنید."), 429

        prize = secrets.choice(PRIZES)
        conn.execute(
            "INSERT INTO spins(g_name,p_name,spun_at,prize) VALUES(?,?,?,?)",
            (g_name, p_name, now.isoformat(), prize)
        )
    return jsonify(ok=True, prize=prize)

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if session.get("admin"):
        return redirect(url_for("dashboard"))
    error = None
    if request.method == "POST":
        g = request.form.get("g", "").strip()
        p = request.form.get("p", "")
        if ADMIN_G and (ADMIN_P_HASH or ADMIN_P) and secrets.compare_digest(g, ADMIN_G) and admin_password_ok(p):
            session.clear()
            session["admin"] = True
            return redirect(url_for("dashboard"))
        error = "اطلاعات ورود درست نیست."
    return render_template("admin_login.html", error=error)

@app.route("/admin/dashboard")
@admin_required
def dashboard():
    with db() as conn:
        rows = conn.execute("SELECT g_name,p_name,spun_at,prize FROM spins ORDER BY id DESC LIMIT 500").fetchall()
    return render_template("dashboard.html", rows=rows)

@app.post("/admin/logout")
@admin_required
def logout():
    session.clear()
    return redirect(url_for("admin_login"))

@app.get("/health")
def health():
    return "ok", 200

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
