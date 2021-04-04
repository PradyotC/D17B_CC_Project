from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import owncloud

def create_app():
	app = Flask(__name__)

	# Change this to your secret key (can be anything, it's for extra protection)
	app.config['SECRET_KEY'] = 'shinde'

	# Enter your database connection details below
	app.config['MYSQL_HOST'] = 'remotemysql.com'
	app.config['MYSQL_PORT'] = 3306
	app.config['MYSQL_USER'] = 'M8TDobkMOx'
	app.config['MYSQL_PASSWORD'] = 'V9qSf4aV4b'
	app.config['MYSQL_DB'] = 'M8TDobkMOx'

	# Intialize MySQL
	mysql = MySQL(app)


	oc = owncloud.Client('http://34.123.27.121/')
	oc.login('user', 'q5XLTik5OPYm')

	# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
	@app.route('/cc/', methods=['GET', 'POST'])
	def login():
	    # Output message if something goes wrong...
	    msg = ''
	    # Check if "username" and "password" POST requests exist (user submitted form)
	    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
	        # Create variables for easy access
	        username = request.form['username']
	        password = request.form['password']
	        # Check if account exists using MySQL
	        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	        cursor.execute('SELECT * FROM user_accounts WHERE username = %s AND password = %s', (username, password, ))
	        # Fetch one record and return result
	        account = cursor.fetchone()
	        # If account exists in accounts table in out database
	        if account:
	            # Create session data, we can access this data in other routes
	            session['loggedin'] = True
	            session['id'] = account['id']
	            session['username'] = account['username']
	            # Redirect to home page
	            return redirect(url_for('home'))
	        else:
	            # Account doesnt exist or username/password incorrect
	            msg = 'Incorrect username/password!'
	    # Show the login form with message (if any)
	    return render_template('index.html', msg=msg)

	# http://localhost:5000/python/logout - this will be the logout page
	@app.route('/cc/logout')
	def logout():
	    # Remove session data, this will log the user out
	   session.pop('loggedin', None)
	   session.pop('id', None)
	   session.pop('username', None)
	   # Redirect to login page
	   return redirect(url_for('login'))

	# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
	@app.route('/cc/register', methods=['GET', 'POST'])
	def register():
	    # Output message if something goes wrong...
	    msg = ''
	    # Check if "username", "password" and "email" POST requests exist (user submitted form)
	    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
	        # Create variables for easy access
	        username = request.form['username']
	        password = request.form['password']

	        # Check if account exists using MySQL
	        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	        cursor.execute('SELECT * FROM user_accounts WHERE username = %s', (username, ))
	        account = cursor.fetchone()
	        # If account exists show error and validation checks
	        if account:
	            msg = 'Account already exists!'
	        elif not re.match(r'[A-Za-z0-9]+', username):
	            msg = 'Username must contain only characters and numbers!'
	        elif not username or not password:
	            msg = 'Please fill out the form!'
	        else:
	            # Account doesnt exists and the form data is valid, now insert new account into accounts table
	            cursor.execute('INSERT INTO user_accounts VALUES (NULL, %s, %s)', (username, password, ))
	            mysql.connection.commit()
	            msg = 'You have successfully registered!'

	    elif request.method == 'POST':
	        # Form is empty... (no POST data)
	        msg = 'Please fill out the form!'
	    # Show registration form with message (if any)
	    return render_template('register.html', msg=msg)

	# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
	@app.route('/cc/home')
	def home():
	    # Check if user is loggedin
	    if 'loggedin' in session:
	        # User is loggedin show them the home page
	        return render_template('home.html', username=session['username'])
	    # User is not loggedin redirect to login page
	    return redirect(url_for('login'))

	@app.route('/cc/home/edit', methods=['GET', 'POST'])
	def edit():	
		msg = ''
		return render_template('edit.html', msg=msg)		

	@app.route('/cc/edit1', methods=['GET','POST'])    
	def edit1():
	    filepath = request.args.get('filepath')
	    text_content = request.args.get('text_content')
	    str1 = oc.get_file_contents(filepath)
	    str2 = bytes(str1.decode('UTF-8') + "\n" + text_content,'UTF-8')
	    oc.put_file_contents(filepath, str2)
	    return {"message":"successful"}

	# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
	@app.route('/cc/profile')
	def profile():
	    # Check if user is loggedin
	    if 'loggedin' in session:
	        # We need all the account info for the user so we can display it on the profile page
	        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	        cursor.execute('SELECT * FROM user_accounts WHERE id = %s', (session['id'],))
	        account = cursor.fetchone()
	        # Show the profile page with account info
	        return render_template('profile.html', account=account)
	    # User is not loggedin redirect to login page
	    return redirect(url_for('login'))


	return app