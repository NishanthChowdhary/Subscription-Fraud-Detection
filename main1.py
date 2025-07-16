from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
import pandas as pd
import time
import csv
import joblib

app = Flask(__name__)
app.secret_key = 'heythisismysubsfraudapp'

model = joblib.load("newfile1.pkl")
# Sample data for products
products = [
    {"id": i, "name": f"Product {i}", "price": i * 10, "description": f"Description for Product {i}", "image": f"product{i}.jpg"} for i in range(1, 101)
]

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('UNAUTHORISED, Please Login', 'danger')
            return redirect(url_for('product_listing'))
    return wrap

def save_interaction_data(data):
    with open('user_interaction_data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

@app.route('/')
def product_listing():
    session['start_time'] = time.time()  # Start session timing
    return render_template('product_list.html')

@app.route('/details/<int:product_id>')
def product_details(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        return render_template('product_details.html', product=product)
    else:
        return "Product not found", 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        if email and email.endswith('@gmail.com'):
            session['logged_in'] = True
            session['email'] = email
            return redirect(session.get('return_page', '/'))
        else:
            flash("Please enter a valid email ending with @gmail.com", "danger")
            return redirect('login')
    return render_template('login.html')

@app.route("/logout")
def logout():
    session['logged_in'] = False
    flash('You are now logged out', 'success')
    return redirect(url_for('product_listing'))

# Analyze user data using pandas
def analyze_user_data(user_email, product_name):
    df = pd.read_csv('user_interaction_data.csv')

    # Calculate repeated attempts
    repeated_attempts = len(df[(df['User_Email'] == user_email) & (df['Product_Name'] == product_name)])

    # Calculate user history (thresholds can be adjusted)
    total_purchases = len(df[df['User_Email'] == user_email])
    if total_purchases > 10:
        # user_history = 'Frequent'
        user_history = 3
    elif total_purchases > 3:
        # user_history = 'Normal'
        user_history = 2
    else:
        # user_history = 'Rare'
        user_history = 1

    # Calculate uncommon service (threshold can be adjusted)
    product_purchases = len(df[df['Product_Name'] == product_name])
    uncommon_service = 1 if product_purchases < 5 else 0

    return len(df)+1, repeated_attempts, user_history, uncommon_service

# Payment page
@app.route('/payment/<int:product_id>', methods=['GET', 'POST'])
def payment(product_id):
    if 'logged_in' not in session:
        session['return_page'] = f'/payment/{product_id}'
        return redirect(url_for('login'))
    
    product = next((p for p in products if p['id'] == product_id), None)
    
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        card = request.form['card']
        order_amount = request.form['amount']
        typing_speed = request.form['typing_speed']
        typing_speed = 0 if typing_speed == 'NaN' else float(typing_speed)
        # Retrieve the tab switch count from sessionStorage via a hidden field
        browser_changes = request.form['browser_changes']
        browser_changes = 0 if browser_changes=='0' else 1
        # Calculate session length
        session_length = time.time() - session['start_time']
        # Analyze user data for repeated attempts, user history, and uncommon service
        transaction_id, repeated_attempts, user_history, uncommon_service = analyze_user_data(session['email'], product['name'])
        # Collect data and save it
        data = [
            # transaction_id,  # Transaction ID as timestamp
            # session['email'],
            # product['name'],
            typing_speed,  # Interaction speed (typing speed)
            repeated_attempts,  # Repeated attempts
            user_history,  # User history
            session_length,  # Session length in seconds
            browser_changes,  # Browser changes (tab switches)
            uncommon_service,  # Uncommon service
            # 0  # Fraud (default 0)
        ]
        save_interaction_data(data)
        print(data)
        prediction = model.predict([data])
        print("Prediction: ", prediction)
        if prediction==1:
            print("Fraud is detected")
        else:
            print("No Fraud is detected")
        if prediction==1:
            flash("FRAUD", "danger")
            return redirect(url_for("product_listing"))
        return redirect(url_for("product_listing"))
    
    return render_template('payment.html', product=product, email=session['email'])

if __name__ == '__main__':
    app.run(debug=False)
