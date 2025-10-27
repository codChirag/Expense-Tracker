from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # change this for security

# ------------------ DATABASE SETUP ------------------
def init_db():
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                category TEXT,
                amount REAL,
                date TEXT
            )
        ''')
        conn.commit()

# ------------------ ROUTES ------------------

@app.route('/')
def home():
    if "user" in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect("database.db") as conn:
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                flash("Account created successfully! Please log in.", "success")
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash("Username already exists. Please try another.", "danger")
                return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect("database.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = cur.fetchone()

            if user:
                session['user'] = username
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid username or password.", "danger")
                return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        flash("Please log in to access your dashboard.", "warning")
        return redirect(url_for('login'))

    username = session["user"]
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT category, amount, date FROM expenses WHERE username=?", (username,))
        data = cur.fetchall()

    return render_template('dashboard.html', username=username, data=data)

@app.route('/add', methods=['POST'])
def add_expense():
    if "user" not in session:
        return redirect(url_for('login'))

    category = request.form['category']
    amount = request.form['amount']
    date = request.form['date']
    username = session["user"]

    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO expenses (username, category, amount, date) VALUES (?, ?, ?, ?)",
                    (username, category, amount, date))
        conn.commit()

    flash("Expense added successfully!", "success")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop("user", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

# ------------------ RUN SERVER ------------------
if __name__ == "__main__":
    init_db()  # Ensure DB tables are created

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
