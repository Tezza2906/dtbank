from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from .db import get_db
from . import bcrypt
from .models import get_customer_by_username

customer_bp = Blueprint("customer", __name__)

@customer_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        account_holder_name = request.form['account_holder_name']
        password = request.form['password']
        DOB = request.form['DOB']
        age = request.form['age']
        gender = request.form['gender']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        balance = 0.00
        interest = float((5/100) * balance)

        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        account_number = 'ACC' + datetime.now().strftime('%Y%m%d%H%MS')

        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("insert into customers (username, acc_holder, password_hash,DOB,age,gender,email,phone,address,account_number,balance, interest) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (username, account_holder_name, hashed, DOB, age, gender, email, phone, address, account_number, balance, interest))
        conn.commit()
        cur.close()
        conn.close()
        if username == '' or email == '' or phone == '' or age == '' or address == '' or password == '' or account_holder_name == '' or DOB == '':
            flash('All fields are required.', 'error')
            return redirect(url_for('customer.register'))
        elif username in get_customer_by_username(username):
            flash('Username already exists.', 'error')
            return redirect(url_for('customer.register'))
        elif email in get_customer_by_username(email):
            flash('Email already exists.', 'error')
            return redirect(url_for('customer.register'))
        elif phone in get_customer_by_username(phone):
            flash('Phone number already exists.', 'error')
            return redirect(url_for('customer.register'))
        elif age<18:
            flash('Minimum age to open an account is 18 years.', 'error')
            return redirect(url_for('customer.register'))
        else:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('customer.login'))
        
    return render_template('customer/register.html')

@customer_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        user = get_customer_by_username(username)
        if user and bcrypt.check_password_hash(user['password_hash'],password):
            session['customer_id'] = user['customer_id']
            session['username'] = user['username']
            session['account_number'] = user['account_number']
            flash('Login successful!', 'success')
            return redirect(url_for('customer.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('customer/login.html')

@customer_bp.route('/dashboard')
def dashboard():
    if "customer_id" not in session:
        return redirect(url_for("customer.login"))

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT username, account_number, balance FROM customers WHERE customer_id = %s",
        (session["customer_id"],),
    )
    acc = cur.fetchone()
    cur.close()
    conn.close()

    if not acc:
        flash("Account not found.", "error")
        return redirect(url_for("customer.login"))

    return render_template(
        "customer/dashboard/main.html",
        username=acc.get("username"),
        account_number=acc.get("account_number"),
        balance=acc.get("balance"),
    )

    # if 'customer_id' not in session:
    #     return redirect(url_for('customer.login'))
    # return render_template('customer/dashboard/main.html')

@customer_bp.route('/dashboard/profile')
def profile():
            if 'customer_id' not in session:
                return redirect(url_for('customer.login'))
            conn = get_db()
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "select acc_holder, username, email, phone,DOB, age, gender,account_number, address, created_at, balance from customers where customer_id = %s", (session['customer_id'],),
            )
            acc = cur.fetchone()
            cur.close()
            conn.close()
            
            return render_template(
                "customer/dashboard/profile.html",
                acc_holder = acc.get('acc_holder'),
                username = acc.get('username'),
                email = acc.get('email'),
                phone = acc.get('phone'),
                DOB = acc.get('DOB'),
                age = acc.get('age'),
                gender = acc.get('gender'),
                account_number = acc['account_number'],
                address = acc.get('address'),
                created_at = acc.get('created_at'),
                balance = acc.get('balance'),
                user=acc

            )
@customer_bp.route('/dashboard/account')
def account():
    if 'customer_id' not in session:
        return redirect(url_for('customer.login'))
    
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
         "select acc_holder, account_number, balance, interest from customers where customer_id = %s", (session['customer_id'],),)
    acc = cur.fetchone()
    cur.close()
    conn.close()

    return render_template(
        'customer/dashboard/account.html',
        acc_holder = acc['acc_holder'],
        account_number = acc['account_number'],
        balance = acc['balance'],
        interest = acc['interest'],

    )
    # else:
    #     def profile():
    #         conn = get_db()
    #         cur = conn.cursor(dictionary=True)
    #         cur.execute(
    #             "select acc_holder, username, email, phone,DOB, age, gender,account_number, address, created_at,  from customers where customer_id = %s", (session['customer_id'],)
    #         )
    #         acc = cur.fetchone()
    #         cur.close()
    #         conn.close()

    #         return render_template(
    #             "customer/dashboard/profile.html",
    #             username = acc.get('username'),
    #             email = acc.get('email'),
    #             phone = acc.get('phone'),
    #             DOB = acc.get('DOB'),
    #             age = acc.get('age'),
    #             gender = acc.get('gender'),
    #             account_number = acc['account_number'],
    #             address = acc.get('address'),
    #             created_at = acc.get('created_at'),
    #         )
        
    #     def account():
            # conn = get_db()
            # cur = conn.cursor(dictionary=True)
            # cur.execute(
            #     'select acc_holder, account_number, balance, interest from customers where customer_id = %s', (session['customer_id'],) 
            # )
            # acc = cur.fetchone()
            # cur.close()
            # conn.close()

            # return render_template(
            #     'customer/dashboard/account.html',
            #     acc_holder = acc['acc_holder'],
            #     account_number = acc['account_number'],
            #     balance = acc['balance'],
            #     interest = acc['interest'],

            # )
@customer_bp.route("/transfer", methods=["GET", "POST"])
def transfer():
    if "customer_id" not in session:
        return redirect(url_for("customer.login"))

    if request.method == "POST":
        sender_id = session["customer_id"]
        recipient_account = request.form.get("recipient_account", "").strip()
        try:
            amount = float(request.form.get("amount", "0"))
        except (TypeError, ValueError):
            flash("Invalid amount.", "error")
            return redirect(url_for("customer.transfer"))

        conn = get_db()
        cur = conn.cursor(dictionary=True)

        try:
            conn.start_transaction()

            # Get sender
            cur.execute(
                "SELECT customer_id, balance FROM customers WHERE customer_id = %s",
                (sender_id,),
            )
            sender = cur.fetchone()
            if not sender:
                conn.rollback()
                flash("Sender account not found.", "error")
                return redirect(url_for("customer.transfer"))

            # Get recipient
            cur.execute(
                "SELECT customer_id, balance FROM customers WHERE account_number = %s",
                (recipient_account,),
            )
            recipient = cur.fetchone()

            if not recipient:
                conn.rollback()
                flash("Recipient account not found.", "error")
                return redirect(url_for("customer.transfer"))

            if recipient["customer_id"] == sender_id:
                conn.rollback()
                flash("Cannot transfer to your own account.", "error")
                return redirect(url_for("customer.transfer"))

            if sender["balance"] < amount:
                conn.rollback()
                flash("Insufficient balance.", "error")
                return redirect(url_for("customer.transfer"))

            
            else:
                #deduct from
                cur.execute("UPDATE customers SET balance = %s WHERE customer_id = %s",(sender["balance"] - amount, sender_id),)
                # Credit recipient
                cur.execute("UPDATE customers SET balance = %s WHERE customer_id = %s",(recipient["balance"] + amount, recipient["customer_id"]),)
                # Transaction for sender (outgoing)
                cur.execute(
                                """
                                INSERT INTO transactions
                                    (customer_id, transaction_type, amount, recipient_account)
                                VALUES (%s, %s, %s, %s)
                                """,
                                (sender_id, "transfer", -amount, recipient_account),
                            )
                # Transaction for recipient (incoming)
                cur.execute(
                                """
                                INSERT INTO transactions
                                    (customer_id, transaction_type, amount, recipient_account)
                                VALUES (%s, %s, %s, %s)
                                """,
                                (recipient["customer_id"], "transfer", amount, None),
                            )
                
                conn.commit()
                flash("Transfer successful!", "success")

            

            

        except Exception as e:
            conn.rollback()
            # For debugging, you can log e
            flash(f"Transaction failed. Please try again. Error: {e}", "error")

        finally:
            cur.close()
            conn.close()

        return redirect(url_for("customer.dashboard"))

    return render_template("customer/transfer.html")

@customer_bp.route('/transactions')
def transactions():
    if 'customer_id' not in session:
        return redirect(url_for('customer.login'))
    
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        'select * from transactions where customer_id = %s order by transaction_date desc', (session['customer_id'],)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('customer/transactions.html', transactions = rows)

@customer_bp.route('/Logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('customer.login'))




        

    




