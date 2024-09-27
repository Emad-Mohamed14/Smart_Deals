from flask import Flask, request, redirect, render_template, session, url_for, flash
from flask_mysqldb import MySQL
import os
import bcrypt
from werkzeug.utils import secure_filename
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure file upload
UPLOAD_FOLDER = 'static/uploads'  # Folder to save uploaded product images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@app.route('/post_product', methods=['GET', 'POST'])
def post_product():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get product details from form
        product_name = request.form['product_name']
        category = request.form['category']
        product_description = request.form['product_description']
        rating = request.form['rating']
        purchase_date = request.form['purchase_date']
        cost_price = request.form['cost_price']
        selling_price = request.form['selling_price']

        # Handle file upload for product image
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        else:
            flash("Invalid image format. Please upload a PNG, JPG, or GIF file.", "danger")
            return redirect(url_for('post_product'))

        try:
            cur = mysql.connection.cursor()
            # Insert product details into the database
            cur.execute('INSERT INTO products (product_name, category, product_description, rating, purchase_date, cost_price, selling_price, image_url, owner_id) '
                        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        (product_name, category, product_description, rating, purchase_date, cost_price, selling_price, file_path, session['user_id']))
            mysql.connection.commit()
            cur.close()
            flash('Product posted successfully!', 'success')
        except Exception as e:
            app.logger.error(f"Error posting product: {e}")
            return "Error occurred", 500
        
        return redirect(url_for('first_webpage'))

    return render_template('post_product.html')

@app.route('/user_profile', methods=['GET'])
def user_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    # Fetch user information and the count of products from the database
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT name, gender, age, address, email, username, COUNT(products.id) as product_count 
        FROM users 
        LEFT JOIN products ON users.id = products.owner_id 
        WHERE users.id = %s 
        GROUP BY users.id
    """, (user_id,))
    user_info = cur.fetchone()
    
    cur.close()
    
    if user_info:
        name, gender, age, address, email, username, product_count = user_info
    else:
        name = gender = age = address = email = username = product_count = None

    return render_template('user_profile.html', 
                           name=name, 
                           gender=gender, 
                           age=age, 
                           address=address, 
                           email=email, 
                           username=username, 
                           product_count=product_count)

@app.route('/product_details/<int:product_id>')
def product_details(product_id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM products WHERE id = %s', (product_id,))
    product = cur.fetchone()
    cur.close()

    if product:
        return render_template('product_details.html', product=product)
    else:
        return "Product not found", 404

@app.route('/first_webpage')
def first_webpage():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products")  # Adjust the query as needed
    products = cur.fetchall()  # Get all products
    cur.close()
    return render_template('first_webpage.html', products=products)

@app.route('/second')
def second():
    return render_template('second.html')

if __name__ == '__main__':
    app.run(debug=True)
