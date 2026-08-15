from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response
from .db import get_db
from . import bcrypt
from .models import get_admin_by_username

admin_bp = Blueprint('admin', __name__)


def admin_required():
    return "admin_id" in session

@admin_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if get_admin_by_username(username):
            flash('Username already exists', 'error')
            return redirect(url_for('admin.register'))

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO admins (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        conn.commit()
        cur.close()
        conn.close()

        flash('Admin registered successfully! Please log in.', 'success')
        return redirect(url_for('admin.login'))

    return render_template('admin/register.html')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = get_admin_by_username(username)
        if admin and bcrypt.check_password_hash(admin['password_hash'], password):
            session['admin_id'] = admin['admin_id']
            session['admin_username'] = admin['username']
            flash('Admin Login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials', 'error')

    return render_template('admin/login.html')

@admin_bp.route('/dashboard')
def dashboard():
    if not admin_required():
        return redirect(url_for('admin.login'))

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT count(*) as total FROM customers')
    total_customers = cur.fetchone()['total']
    cur.execute("select sum(balance) as total_balance from customers")
    total_balance = cur.fetchone()['total_balance'] or 0
    cur.execute("select * from transactions order by transaction_date desc limit 10")
    recent= cur.fetchall()
    cur.close()
    conn.close()

    return render_template(
        'admin/dashboard.html',
        total_customers=total_customers,
        total_balance=total_balance,
        recent_transactions=recent,
    )

@admin_bp.route('/users')
def users():
    if not admin_required():
        return redirect(url_for('admin.login'))
    
    conn= get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT customer_id, acc_holder, username, email, phone, account_number, balance, created_at FROM customers order by created_at desc")
    
    customers = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('admin/users.html', customers=customers)

@admin_bp.route('transactions')
def transactions():
    if not admin_required():
        return redirect(url_for('admin.login'))
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("select t.*, c.username from transactions t join customers c on t.customer_id = c.customer_id order by transaction_date desc")

    txns = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('admin/transactions.html', transactions=txns)

@admin_bp.route('/logout')
def logout():
    session.clear()
    flash('Admin logged out successfully', 'success')
    return redirect(url_for('admin.login'))


@admin_bp.route("/add-money/<int:customer_id>", methods=["GET", "POST"])
def add_money(customer_id):
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    # Get customer info
    cur.execute(
        "SELECT customer_id, acc_holder, balance FROM customers WHERE customer_id = %s",
        (customer_id,),
    )
    customer = cur.fetchone()

    if not customer:
        cur.close()
        conn.close()
        flash("Customer not found.", "error")
        return redirect(url_for("admin.users"))

    if request.method == "POST":
        # 1. Read amount safely
        amount_raw = request.form.get("amount")
        try:
            amount = float(amount_raw)
        except (TypeError, ValueError):
            flash("Invalid amount.", "error")
            cur.close()
            conn.close()
            return redirect(url_for("admin.add_money", customer_id=customer_id))

        # 2. Validate amount
        if amount <= 0:
            flash("Amount must be greater than zero.", "error")
            cur.close()
            conn.close()
            return redirect(url_for("admin.add_money", customer_id=customer_id))

        # 3. Update balance
        cur.execute(
            "UPDATE customers SET balance = balance + %s WHERE customer_id = %s",
            (amount, customer_id),
        )

        # 4. Optional transaction log
        cur.execute(
            """
            INSERT INTO transactions
                (customer_id, transaction_type, amount, recipient_account)
            VALUES (%s, %s, %s, %s)
            """,
            (customer_id, "credit", amount, None),
        )

        conn.commit()
        cur.close()
        conn.close()

        flash(f"₹{amount:.2f} added to {customer['acc_holder']}'s account.", "success")
        return redirect(url_for("admin.users"))  # Success path

    # GET: show form
    cur.close()
    conn.close()
    return render_template("admin/add_money.html", customer=customer)
    
