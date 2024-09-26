from flask import Flask, request, redirect, render_template, session, url_for
from flask_mysqldb import MySQL
import os
import bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24)

logging.basicConfig(filename='check.log',  # Specify the log file
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

logging.debug("Logging is working!")

# MySQL configurations
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "tsee12345"
app.config['MYSQL_DB'] = "smart_deals"

mysql = MySQL(app)

def check_db_connection():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        cur.close()
        return True
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        return False

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Collecting form data
        name = request.form['name']
        gender = request.form['gender']
        age = request.form['age']
        address = request.form['address']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password'].encode('utf-8')  # Encode password for hashing
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())  # Hash the password
        
        try:
            # Insert user into the database
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO users (name, gender, age, address, email, username, password1) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                        (name, gender, age, address, email, username, hashed_password))
            mysql.connection.commit()
            cur.close()
        except Exception as e:
            app.logger.error(f"Error inserting into database: {e}")
            return "Error occurred", 500
        
        return redirect(url_for('login'))  # Redirect to login after signup

    return render_template('signup.html')  # Render signup form

@app.route('/login', methods=['GET', 'POST'])
def login():
    logging.debug("Login route accessed.")

    if request.method == 'POST':
        logging.debug("POST request detected.")
        username = request.form['username']
        password = request.form['password']
        logging.debug(f"Form submitted with username: {username}")

        try:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = cur.fetchone()
            cur.close()

            # Log result from the database
            if user:
                logging.debug(f"User found: {user}")
            else:
                logging.debug(f"No user found with username: {username}")

            if user and bcrypt.checkpw(password.encode('utf-8'), user[7].encode('utf-8')):
                session['user_id'] = user[0]
                logging.debug(f"User {username} logged in successfully.")
                return redirect('/first_webpage')
            else:
                logging.warning(f"Login failed for username: {username} - Invalid credentials")
                return "Invalid credentials", 401
            
        except Exception as e:
            logging.error(f"Error occurred during login: {str(e)}")
            return "Error occurred", 500
    
    return render_template('login.html')  # Render login form

@app.route('/first_webpage')
def first_webpage():
    return render_template('first_webpage.html')

@app.route('/product/<int:product_id>')
def product_details(product_id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM products WHERE id = %s', (product_id,))
    product = cur.fetchone()
    
    if product:
        cur.execute('SELECT username FROM users WHERE id = %s', (product[5],))  # Get seller info
        seller = cur.fetchone()
        return render_template('second.html', product=product, seller=seller)

    return "Product not found", 404  # Handle case if product not found

# Add more routes as needed

if __name__ == '__main__':
    app.run(debug=True)
