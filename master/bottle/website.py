## Import dependencies
# Import external modules
import hashlib, pymongo, pytz
from flask import (
	Blueprint,
	request,
	redirect,
	render_template,
	session,
	url_for
)
from bson.objectid import ObjectId
from datetime import datetime

# Import own modules
from ..mongosetup import *


## Initialise app
website = Blueprint(
	"website",
	__name__,
	template_folder="../../templates"
)


## Useful functions & variables
def dev_problem():
	'''
	This function is only triggered if one of the developers (aka. either Christopher of Renoir) made a mistake in the code that results in our code not working. It is placed at the end of each function, and when triggered it renders a 404 error page.


	Parameters:
		NIL

	Returns:
		flask.render_template: Renders the 404 error page that informs the user that the developers have made an error somewhere in the code.
			filename (str): The file name of the html file to be rendered. (404-depression.html)
			logged_in_user (str): The username of the logged in user.
			error_text (str): The error text to be displayed to the user on the error page.
	'''
	return render_template(
		"404-depression.html",
		logged_in_user=session.get("logged_in_user"),
		error_text="Something went wrong. Go blame the devs."
	)

def encode_sha256(string, rounds=1):
	'''
	This function is a custom SHA-256 encoder, which packages the hashlib.sha256 encoder in a for loop to encode using SHA-256 as many times as needed.


	Parameters:
		string (str): The string that is to be encoded.
		rounds (int = 1): The number of times that the string should be encoded.
	
	Returns:
		encoded (str): The encoded string
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	encoded = string
	for i in range(rounds):
		encoded = hashlib.sha256((string).encode()).hexdigest()
	return encoded
	return dev_problem()

def make_encrypted_user_pass(username, password):
	'''
	This function contains our algorithm for encoding passwords.

	encrypted_user_pass is derived by running the username and password individually through SHA-256 hashing, then concatenating the hashed username and password and running the result through SHA-256 hashing.

	Only encrypted_user_pass is stored in MongoDB for security purposes, dummy passwords are stored in 'notes/dummy_info.md' for testing purposes


	Parameters:
		username (str): The username to be encoded.
		password (str): The password to be encoded

	Returns:
		encrypted_user_pass (str): The encrypted output of the username and password, which is either input into MongoDB or used to check against an encrypted_user_pass stored in mongo to login a user.
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	return encode_sha256(
		encode_sha256(username) + encode_sha256(password)
	)
	return dev_problem()

sg_timezone = pytz.timezone("Asia/Singapore")
def aware_datetime(utc_time):
	'''
	This function converts the current date and time in UTC to SGT (UTC+8).


	Parameters:
		utc_time (datetime): The current date and time in UTC.

	Returns:
		sgt_time (datetime): The current date and time in SGT (UTC+8).
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	return utc_time.replace(tzinfo=pytz.utc).astimezone(sg_timezone)
	return dev_problem()

# A variable with a list of usernames of accounts with administrative access to the website.
admin_access = ["dummyStudent", "dummyStaff"]


## Website routes
# Homepage
@website.route("/", methods=["GET"])
def homepage():
	'''
	This function renders the homepage of the website.


	Parameters:
		NIL

	Returns:
		flask.render_template: Renders the homepage.
			filename (str): The file name of the html file to be rendered. (homepage.html)
			logged_in_user (str): The username of the logged in user.
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if request.method == "GET":
		return render_template(
			"homepage.html",
			logged_in_user=session.get("logged_in_user")
		)
	return dev_problem()

# Login pages
@website.route("/login", methods=["GET"])
def login():
	'''
	This function redirects from the general login page to the student login page.


	Parameters:
		NIL

	Returns:
		flask.redirect: Redirects the user to the student login page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (student_login())
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if request.method == "GET":
		return redirect(url_for("website.student_login"))
	return dev_problem()

@website.route("/login/student", methods=["GET", "POST"])
def student_login():
	'''
	This function either
		renders the student login page of the website if the user is not logged in,
		redirects the user from the student login page to the homepage if the user is logged in, or
		redirects the user from the student login page to the invalid login page if the user gave incorrect login credentials.
	
	If the user is not logged in and tries to login, the username and password they input is encrypted and checked against the encryped_user_pass of students in the MongoDB database. If the login credentials are correct, meaning the username and encryped_user_pass match up with that of a student user, they are logged in as that student user and redirected to the homepage of the website.


	Parameters:
		NIL

	Returns:
		flask.render_template: Renders the student login page.
			filename (str): The file name of the html file to be rendered. (login-student.html)
			logged_in_user (str): The username of the logged in user.
		OR
		flask.redirect: Redirects the user to the homepage.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (homepage())
		OR
		flask.redirect: Redirects the user to the invalid login page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (invalid_login())
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if request.method == "GET":
		if "logged_in_user" not in session:
			return render_template(
				"login-student.html",
				logged_in_user=session.get("logged_in_user")
			)
		else:
			return redirect(url_for("website.homepage"))
	elif request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		encryptedUserPass = make_encrypted_user_pass(
			username,
			password
		)
		query = {
			"encryptedUserPass": encryptedUserPass
		}
		result = COLLECTIONS["students"].find_one(query)
		if result != None:
			session["logged_in_user"] = result["username"]
			session["user_type"] = "STUDENT"
			print(f"Session: {session}")
			print(f"Session Login: {session['logged_in_user']}")
			return redirect(url_for("website.homepage"))
		else:
			return redirect(url_for("website.invalid_login"))
	return dev_problem()

@website.route("/login/staff", methods=["GET", "POST"])
def staff_login():
	'''
	This function either
		renders the staff login page of the website if the user is not logged in,
		redirects the user from the staff login page to the homepage if the user is logged in, or
		redirects the user from the staff login page to the invalid login page if the user gave incorrect login credentials.
	
	If the user is not logged in and tries to login, the username and password they input is encrypted and checked against the encryped_user_pass of staff in the MongoDB database. If the login credentials are correct, meaning the username and encryped_user_pass match up with that of a staff user, they are logged in as that staff user and redirected to the homepage of the website.


	Parameters:
		NIL

	Returns:
		flask.render_template: Renders the staff login page.
			filename (str): The file name of the html file to be rendered. (login-staff.html)
			logged_in_user (str): The username of the logged in user.
		OR
		flask.redirect: Redirects the user to the homepage.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (homepage())
		OR
		flask.redirect: Redirects the user to the invalid login page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (invalid_login())
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if request.method == "GET":
		if "logged_in_user" not in session:
			return render_template(
				"login-staff.html",
				logged_in_user=session.get("logged_in_user")
			)
		else:
			return redirect(url_for("website.homepage"))
	elif request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		encryptedUserPass = make_encrypted_user_pass(
			username,
			password
		)
		query = {
			"encryptedUserPass": encryptedUserPass
		}
		result = COLLECTIONS["staff"].find_one(query)
		if result != None:
			session["logged_in_user"] = result["username"]
			session["user_type"] = "STAFF"
			return redirect(url_for("website.homepage"))
		else:
			return redirect(url_for("website.invalid_login"))
	return dev_problem()

@website.route("/login/invalid", methods=["GET"])
def invalid_login():
	'''
	This function either
		renders the invalid login page of the website if the user is not logged in or
		redirects the user from the invalid login page to the homepage if the user is logged in.


	Parameters:
		NIL

	Returns:
		flask.render_template: Renders the invalid login page.
			filename (str): The file name of the html file to be rendered. (login-invalid.html)
			logged_in_user (str): The username of the logged in user.
		OR
		flask.redirect: Redirects the user to the homepage.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (homepage())
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if "logged_in_user" not in session:
		return render_template(
			"login-invalid.html",
			logged_in_user=session.get("logged_in_user")
		)
	else:
		if request.method == "GET":
			return redirect(url_for("website.homepage"))
	return dev_problem()

@website.route("/logout", methods=["GET"])
def logout():
	'''
	This function either
		renders the logout page of the website if the user is logged in or
		redirects the user from the logout page to the homepage if the user is not logged in.


	Parameters:
		NIL

	Returns:
		flask.render_template: Renders the logout page.
			filename (str): The file name of the html file to be rendered. (logout.html)
		OR
		flask.redirect: Redirects the user to the homepage.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (homepage())
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if "logged_in_user" in session:
		session.clear()
		return render_template("logout.html")
	else:
		if request.method == "GET":
			return redirect(url_for("website.homepage"))
	return dev_problem()


# Create new users
@website.route("/user", methods=["GET"])
def user():
	'''
	This function redirects from the user page to the create new user page.


	Parameters:
		NIL

	Returns:
		flask.redirect: Redirects the user to the create new user page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (create_user())
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if request.method == "GET":
		return redirect(url_for("website.create_user"))
	return dev_problem()

@website.route("/user/create", methods=["GET"])
def create_user():
	'''
	This function redirects from the create new user page to the create new student page.


	Parameters:
		NIL

	Returns:
		flask.redirect: Redirects the user to the create new student page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (create_student())
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if request.method == "GET":
		return redirect(url_for("website.create_student"))
	return dev_problem()

@website.route("/user/create/student", methods=["GET", "POST"])
def create_student():
	'''
	This function exists to make it easier for the administrators to be able to easily add student users, instead of adding them directly through MongoDB Compass or the command line instead.

	This function either
		redirects the user from the create new student page to the login page if the user is not logged in,
		redirects the user from the create new student page to the homepage if the user does not have administrative access,
		renders the create new student page of the website if the user is logged in and has administrative access, or
		redirects the user from the create new student page to itself if a new student user has been created.
	
	If the user is logged in, has administrative access, and makes a request to create a new student, a new student user is added to MongoDB, with the respective username, encryped_user_pass (derived from encrypting the username and password), name, and date_updated (which is when the request was made). The user is then redirected from the create new student page to itself, for ease of adding multiple student users at once.


	Parameters:
		NIL

	Returns:
		flask.redirect: Redirects the user to the login page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (login())
		OR
		flask.redirect: Redirects the user to the homepage.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (homepage())
		OR
		flask.render_template: Renders the create new student page.
			filename (str): The file name of the html file to be rendered. (user-create-student.html)
			logged_in_user (str): The username of the logged in user.
			
		OR
		flask.redirect: Redirects the user to the create new student page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (create_student())
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if "logged_in_user" not in session:
		return redirect(url_for("website.login"))
	elif session["logged_in_user"] not in admin_access:
		return redirect(url_for("website.homepage"))
	else:
		if request.method == "GET":
			return render_template(
				"user-create-student.html",
				logged_in_user=session.get("logged_in_user")
			)
		elif request.method == "POST":
			username = request.form["username"]
			password = request.form["password"]
			COLLECTIONS["students"].insert_one({
				"username": username,
				"encryptedUserPass": make_encrypted_user_pass(
					username,
					password
				),
				"name": request.form["name"],
				"dateUpdated": datetime.now()
			})
			return redirect(url_for("website.create_student"))
	return dev_problem()

@website.route("/user/create/staff", methods=["GET", "POST"])
def create_staff():
	'''
	This function exists to make it easier for the administrators to be able to easily add staff users, instead of adding them directly through MongoDB Compass or the command line instead.
	
	This function either
		redirects the user from the create new staff page to the login page if the user is not logged in,
		redirects the user from the create new staff page to the homepage if the user does not have administrative access,
		renders the create new staff page of the website if the user is logged in and has administrative access, or
		redirects the user from the create new staff page to itself if a new staff user has been created.
	
	If the user is logged in, has administrative access, and makes a request to create a new staff, a new staff user is added to MongoDB, with the respective username, encryped_user_pass (derived from encrypting the username and password), prefix, name, alias, and date_updated (which is when the request was made). The user is then redirected from the create new staff page to itself, for ease of adding multiple staff users at once.


	Parameters:
		NIL

	Returns:
		flask.redirect: Redirects the user to the login page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (login())
		OR
		flask.redirect: Redirects the user to the homepage.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (homepage())
		OR
		flask.render_template: Renders the create new staff page.
			filename (str): The file name of the html file to be rendered. (user-create-staff.html)
			logged_in_user (str): The username of the logged in user.
		OR
		flask.redirect: Redirects the user to the create new staff page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (create_staff())
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if "logged_in_user" not in session:
		return redirect(url_for("website.login"))
	elif session["logged_in_user"] not in admin_access:
		return redirect(url_for("website.homepage"))
	else:
		if request.method == "GET":
			return render_template(
				"user-create-staff.html",
				logged_in_user=session.get("logged_in_user")
			)
		elif request.method == "POST":
			username = request.form["username"]
			password = request.form["password"]
			prefix = request.form["prefix"]
			name = request.form["name"]
			alias = request.form["alias"]
			if alias == "":
				if prefix == "":
					alias = name
				else:
					alias = f"{prefix} {name}"
			COLLECTIONS["staff"].insert_one({
				username: username,
				encryptedUserPass: make_encrypted_user_pass(
					username,
					password
				),
				prefix: prefix,
				name: name,
				alias: alias,
				dateUpdated: datetime.now()
			})
			return redirect(url_for("website.create_staff"))
	return dev_problem()


# Announcements
@website.route("/announcements/", methods=["GET"])
def general_announcements():
	'''
	This function either
		redirects the user from the general announcements page to the login page if the user is not logged in or
		renders the general announcements page of the website if the user is logged in.
	
	To fetch the announcements to be displayed, the function first gets the id of the logged in user, followed by the groups the user is in. Next the forms collection in out MongoDB datatbase is queried to get the 10 most recent announcements that are either for all users or in the list of groups the user is in. 
	
	This announcement data is then passed into the template and rendered as 10 seperate announcements, each displaying the announcement title and date posted.
	
	To view the next/previous 10 announcements, the user can click the right/left arrows at the bottom of the screen, resulting in the page number being incremented/reduced by 1, and the query adjusted accordingly to display the respective announcements.
	

	Parameters:
		NIL

	Returns:
		flask.redirect: Redirects the user to the login page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (login())
		OR
		flask.render_template: Renders the general announcements page.
			filename (str): The file name of the html file to be rendered. (announcements.html)
			logged_in_user (str): The username of the logged in user.
			announcements (list): The list of announcements.
				announcement (dict): The announcement data of an announcement.
			page_number (int): The general announcements page number.
			valid_user_type (bool): The toggle used to decide whether or not to display the create announcement button.
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if "logged_in_user" not in session:
		return redirect(url_for("website.login"))
	else:
		if request.method == "GET":
			# Pages Setup (10 Announcements per page)
			options = dict(request.args)
			if "page" not in options.keys():
				page = 0
				displayed_page = 0
			else:
				page = int(options["page"])
				displayed_page = page
				if page < 0:
					page = 0
			# Get user_id and collection
			if session["user_type"] == "STUDENT":
				collection = "studentsGroup"
				user_id = COLLECTIONS["students"].find_one(
					{"username": session.get("logged_in_user")},
					{"_id": 1}
				)["_id"]
			elif session["user_type"] == "STAFF":
				collection = "staffGroup"
				user_id = COLLECTIONS["staff"].find_one(
					{"username": session.get("logged_in_user")},
					{"_id": 1}
				)["_id"]
			else:
				return dev_problem()
			# Get list of groups user is in
			in_group = COLLECTIONS[collection].find(
				{session.get("user_type").lower(): user_id},
				{"_id": 0, "group": 1}
			)
			group_list = [None]
			for group in in_group:
				group_list.append(group["group"])
			# Get announcement data
			announcements = list(COLLECTIONS["forms"].find({
				"type": "announcement",
				"targetGroup": {"$in": group_list}
			}).sort("_id", -1).skip(page*10).limit(10))
			# Convert date and time from UTC to SGT
			for announcement in announcements:
				announcement["datePosted"] = aware_datetime(announcement["datePosted"])
			# Pass data into template
			return render_template(
				"announcements.html",
				logged_in_user=session.get("logged_in_user"),
				announcements=announcements,
				page_number=displayed_page,
				valid_user_type=(session["user_type"] == "STAFF")
			)
	return dev_problem()

@website.route("/announcement/<id>", methods=["GET", "POST"])
def individual_announcement(id):
	'''
	This function either
		redirects the user from the individual announcement page to the login page if the user is not logged in,
		renders the individual announcement page of the website if the user is logged in,
		renders the 404 error page of the website if the user does not have access to see the announcement, or
		renders the 404 error page of the website if the user tries to access a nonexistent announcement.
		
	To fetch the announcement to be displayed, the function first gets the id of the logged in user, followed by querying forms collection in out MongoDB datatbase is queried to get the announcement data. Then, the function checks if tha announcement is targeted at a specifc group, and if so checks if the logged in user is in that group. 
	
	If the user is in the target group, the announcement will be displayed. If the announcement has no target group stated, it is assumed to be meant for all users, and hence displayed to all users.
	

	Parameters:
		id (str): The id of the announcement the user is trying to view.

	Returns:
		flask.redirect: Redirects the user to the login page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (login())
		OR
		flask.render_template: Renders the individual announcement page.
			filename (str): The file name of the html file to be rendered. (announcement-individual.html)
			logged_in_user (str): The username of the logged in user.
			announcement_data (dict): The data of the announcement.
			author_data (dict): The data of the author of the announcement.
			user_type (str): The type of the user accessing the page. Used to determine whether to display the "Mark as Read" button or the list of students who have read the announcement.
			user_read (bool): The toggle to determine whether or not to display the "Mark as Read" button to students, based on whether the user has already clicked on that button before.
			bluetickers (list): The list of students who have marked the announcement as read.
				blueticker (dict): The dictionary containing the username and name of a student who has read the announcement, and the date the student read it.
		OR
		flask.render_template: Renders the 404 error page that informs the user that they are not in the target group of the announcement and hence, is not allowed to see it.
			filename (str): The file name of the html file to be rendered. (404-depression.html)
			logged_in_user (str): The username of the logged in user.
			error_text (str): The error text to be displayed to the user on the error page. ("You are not supposed to see that announcement.")
		OR
		flask.render_template: Renders the 404 error page that informs the user that they are trying to access a nonexistent announcement.
			filename (str): The file name of the html file to be rendered. (404-depression.html)
			logged_in_user (str): The username of the logged in user.
			error_text (str): The error text to be displayed to the user on the error page. ("You likely used an invalid announcement id.")
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if "logged_in_user" not in session:
		return redirect(url_for("website.login"))
	else:
		# Get user_id
		if session["user_type"] == "STUDENT":
			user_id = COLLECTIONS["students"].find_one(
				{"username": session.get("logged_in_user")},
				{"_id": 1}
			)["_id"]
		elif session["user_type"] == "STAFF":
			user_id = COLLECTIONS["staff"].find_one(
				{"username": session.get("logged_in_user")},
				{"_id": 1}
			)["_id"]
		else:
			return dev_problem()
		# Check if user has read announcement
		user_read = COLLECTIONS["forms"].find_one({
			"_id": ObjectId(id),
			"bluetick.reader": user_id
		}) != None
		if request.method == "GET":
			# Get the announcment data here
			result = COLLECTIONS["forms"].find_one(
				{"_id": ObjectId(id)}
			)
			if result != None:
				# Convert date and time from UTC to SGT
				result["datePosted"] = aware_datetime(result["datePosted"])
				# Check if user is in target group, if specified
				if "targetGroup" in result:
					# Target group specified
					if session["user_type"] == "STUDENT":
						in_target_group = COLLECTIONS["studentsGroup"].find_one({
							"student": user_id,
							"group": result["targetGroup"]
						}) != None
					elif session["user_type"] == "STAFF":
						in_target_group = COLLECTIONS["staffGroup"].find_one({
							"staff": user_id,
							"group": result["targetGroup"]
						}) != None
					else:
						return dev_problem()
				if ("targetGroup" not in result) or (in_target_group):
					# No target group or user in target group
					author_data = COLLECTIONS["staff"].find_one(
						{"_id": result["author"]}
					)
					bluetickers = COLLECTIONS["forms"].find_one(
						{"_id": ObjectId(id)},
						{"_id": 0, "bluetick": 1}
					)["bluetick"]
					for blueticker in bluetickers:
						details = COLLECTIONS["students"].find_one(
							{"_id": blueticker["reader"]},
							{"_id": 0, "username": 1, "name": 1}
						)
						blueticker["username"] = details["username"]
						blueticker["name"] = details["name"]
						# Convert date and time from UTC to SGT
						blueticker["dateRead"] = aware_datetime(blueticker["dateRead"])
					# Pass data into template
					return render_template(
						"announcement-individual.html",
						logged_in_user=session.get("logged_in_user"),
						announcement_data=result,
						author_data=author_data,
						user_type=session["user_type"],
						user_read=user_read,
						bluetickers=bluetickers
					)
				else:
					# Render error template if user not supposed to access
					return render_template(
						"404-depression.html",
						logged_in_user=session.get("logged_in_user"),
						error_text="You are not supposed to see that announcement."
					)
			else:
				# Render error template if user used nonexistent announcement id
				return render_template(
					"404-depression.html",
					logged_in_user=session.get("logged_in_user"),
					error_text="You likely used an invalid announcement id."
				)
		elif request.method == "POST":
			if user_read == False:
				COLLECTIONS["forms"].update_one(
					{"_id": ObjectId(id)},
					{"$push": {"bluetick": {
						"reader": user_id,
						"dateRead": aware_datetime(datetime.utcnow())
					}}}
				)
			return redirect(url_for("website.individual_announcement", id=id))
	return dev_problem()

@website.route("/announcement/post", methods=["GET", "POST"])
def post_annoncement():
	'''
	This function either
		redirects the user from the post announcement page to the login page if the user is not logged in,
		redirects the user from the post announcement page to the general announcements page if the user is not a staff user,
		renders the post announcement page of the website if the user is logged in and is a staff user, or
		redirects the user from the post announcement page to the successful announcement page if the user is not a staff user.
	
	When a staff user wants to post an announcement, they input the announcement title and the body text (where markdown can be used). They can also select if they want the announcement to be directed at a specific group they're in, or at every user.

	The announcement data is parsed and input as a document into the forms collection in out MongoDB database, and the user is then redirected to a successful announcement page, indicating that the announcement had been posted.
	

	Parameters:
		NIL

	Returns:
		flask.redirect: Redirects the user to the login page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (login())
		OR
		flask.redirect: Redirects the user to the general announcements page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (general_announcements())
		OR
		flask.render_template: Renders the post announcement page.
			filename (str): The file name of the html file to be rendered. (announcement-post.html)
			logged_in_user (str): The username of the logged in user.
			groups (list): The list of groups that the user is in.
				group (dict): The dictionary containing data about a group the user is in.
		OR
		flask.redirect: Redirects the user to the successful announcement page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (successful_announcement())
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if "logged_in_user" not in session:
		return redirect(url_for("website.login"))
	else:
		if request.method == "GET":
			if session["user_type"] != "STAFF":
				return redirect(url_for("website.general_announcements"))
			else:
				# Get user_id
				user_id = COLLECTIONS["staff"].find_one(
					{"username": session.get("logged_in_user")},
					{"_id": 1}
				)["_id"]
				# Get list of groups that staff user is in
				in_group = COLLECTIONS["staffGroup"].find(
					{session.get("user_type").lower(): user_id},
					{"_id": 0, "group": 1}
				)
				group_list = []
				for group in in_group:
					group_list.append(group["group"])
				# Get groups
				groups = list(
					COLLECTIONS["groups"].find(
						{"_id": {"$in": group_list}}
					).sort("dateUpdated", -1)
				)
				groups.insert(0, {
					"_id": "",
					"name": "No Group"
				})
				return render_template(
					"announcement-post.html",
					logged_in_user=session.get("logged_in_user"),
					groups=groups
				)
		elif request.method == "POST":
			title = request.form["title"]
			body = request.form["body"]
			author = COLLECTIONS["staff"].find_one(
				{"username": session.get("logged_in_user")}
			)
			date_posted = datetime.now()
			document = {
				"type": "announcement",
				"title": title,
				"body": body,
				"author": author["_id"],
				"datePosted": date_posted,
				"bluetick": []
			}
			if request.form["target-group"] != "":
				document["targetGroup"] = ObjectId(request.form["target-group"])
			document = COLLECTIONS["forms"].insert_one(document)
			return redirect(url_for(
				"website.successful_announcement",
				announcement_id=str(document.inserted_id)
			))
	return dev_problem()

@website.route("/announcement/post/successful", methods=["GET"])
def successful_announcement():
	'''
	This function either
		redirects the user from the successful announcement page to the login page if the user is not logged in or
		renders the post announcement page of the website if the user is logged in and is a staff user.
	
	This page redirects from the post announcement page, and has a button which the user can click to redirect to the announcement that was just posted. If a user visits the page by itself and clicks the aforementioned button, they are instead redirected to the first announcement posted, titled "Welcome to Students Gateway!".
	

	Parameters:
		NIL

	Returns:
		flask.redirect: Redirects the user to the login page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (login())
		OR
		flask.render_template: Renders the post announcement page.
			filename (str): The file name of the html file to be rendered. (announcement-post.html)
			logged_in_user (str): The username of the logged in user.
			groups (list): The list of groups that the user is in.
				group (dict): The dictionary containing data about a group the user is in.
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if "logged_in_user" not in session:
		return redirect(url_for("website.login"))
	else:
		if request.args.get("announcement_id") == None:
			announcement_id = "5f5c5f7dfe40237dbf07b578"
		else:
			announcement_id = request.args.get("announcement_id")
		if request.method == "GET":
			return render_template(
				"announcement-successful.html",
				logged_in_user=session.get("logged_in_user"),
				announcement_id=announcement_id
			)
	return dev_problem()


# Groups
@website.route("/groups/", methods=["GET"])
def groups():
	'''
	This function either
		redirects the user from the general groups page to the login page if the user is not logged in or
		renders the general groups page of the website if the user is logged in.
	
	To fetch the groups to be displayed, the function first gets the id of the logged in user. Next the groups collection in out MongoDB datatbase is queried to get 10 groups. 
	
	This group data is then passed into the template and rendered as 10 seperate groups, each displaying the group name and the date and time of when it was last updated.
	
	To view the next/previous 10 groups, the user can click the right/left arrows at the bottom of the screen, resulting in the page number being incremented/reduced by 1, and the query adjusted accordingly to display the respective groups.
	

	Parameters:
		NIL

	Returns:
		flask.redirect: Redirects the user to the login page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (login())
		OR
		flask.render_template: Renders the general groups page.
			filename (str): The file name of the html file to be rendered. (groups.html)
			logged_in_user (str): The username of the logged in user.
			group (list): The list of groups.
				group (dict): The group data of a group.
			page_number (int): The general groups page number.
			valid_user_type (bool): The toggle used to decide whether ot not to display the create group button.
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if "logged_in_user" not in session:
		return redirect(url_for("website.login"))
	else:
		if request.method == "GET":
			# Pages Setup (10 Groups per page)
			options = dict(request.args)
			if "page" not in options.keys():
				page = 0
				displayed_page = 0
			else:
				page = int(options["page"])
				displayed_page = page
				if page < 0:
					page = 0
			# Get user_id and collection
			if session["user_type"] == "STUDENT":
				collection = "studentsGroup"
				user_id = COLLECTIONS["students"].find_one(
					{"username": session.get("logged_in_user")},
					{"_id": 1}
				)["_id"]
			elif session["user_type"] == "STAFF":
				collection = "staffGroup"
				user_id = COLLECTIONS["staff"].find_one(
					{"username": session.get("logged_in_user")},
					{"_id": 1}
				)["_id"]
			else:
				return dev_problem()
			# Get list of groups user is in
			in_group = COLLECTIONS[collection].find(
				{session.get("user_type").lower(): user_id},
				{"_id": 0, "group": 1}
			)
			group_list = []
			for group in in_group:
				group_list.append(group["group"])
			# Get groups
			groups = list(COLLECTIONS["groups"].find(
				{"_id": {"$in": group_list}}
			).sort("name", 1).skip(page*10).limit(10))
			for group in groups:
				group["dateUpdated"] = aware_datetime(group["dateUpdated"])
			return render_template(
				"groups.html",
				logged_in_user=session.get("logged_in_user"),
				groups=groups,
				page_number=displayed_page,
				valid_user_type=(session["user_type"] == "STAFF")
			)
	return dev_problem()

@website.route("/group/<id>", methods=["GET", "POST"])
def individual_group(id):
	'''
	This function either
		redirects the user from the individual group page to the login page if the user is not logged in,
		renders the individual group page of the website if the user is logged in,
		renders the 404 error page of the website if the user does not have access to see the group, or
		renders the 404 error page of the website if the user tries to access a nonexistent group.
		
	To fetch the group to be displayed, the function first gets the group data. After checking that the group is a valid one, the function then gets the id of the logged in user, and checks if the user is in the group. If so, the student and staff data is retrieved and the page rendered.


	Parameters:
		id (str): The id of the group the user is trying to view.

	Returns:
		flask.redirect: Redirects the user to the login page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (login())
		OR
		flask.render_template: Renders the individual group page.
			filename (str): The file name of the html file to be rendered. (group-individual.html)
			logged_in_user (str): The username of the logged in user.
			group_data (dict): The data of the group.
			students_data (list): The list containing the data of each student user in the group.
				student (dict): The dictionary containing the username and name of the student user.
			staff_data (list): The list containing the data of each staff user in the group. 
				staff (dict): The dictionary containing the username and alias of the staff user.
			valid_user_type (bool): The toggle used to decide whether or not to display the buttons and fields used to modify the group.
		OR
		flask.render_template: Renders the 404 error page that informs the user that they are not in the group they are trying to access.
			filename (str): The file name of the html file to be rendered. (404-depression.html)
			logged_in_user (str): The username of the logged in user.
			error_text (str): The error text to be displayed to the user on the error page. ("You're not in that group buddy.")
		OR
		flask.render_template: Renders the 404 error page that informs the user that they are trying to access a nonexistent group.
			filename (str): The file name of the html file to be rendered. (404-depression.html)
			logged_in_user (str): The username of the logged in user.
			error_text (str): The error text to be displayed to the user on the error page. ("You likely used an invalid group id.")
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if "logged_in_user" not in session:
		return redirect(url_for("website.login"))
	else:
		if request.method == "GET":
			# Get the group data here
			result = COLLECTIONS["groups"].find_one(
				{"_id": ObjectId(id)}
			)
			# Process data
			if result != None:
				# Change date and time from UTC to SGT
				result["dateUpdated"] = aware_datetime(result["dateUpdated"])
				# Get user_id
				if session["user_type"] == "STUDENT":
					collection = "studentsGroup"
					user_id = COLLECTIONS["students"].find_one(
						{"username": session.get("logged_in_user")},
						{"_id": 1}
					)["_id"]
				elif session["user_type"] == "STAFF":
					collection = "staffGroup"
					user_id = COLLECTIONS["staff"].find_one(
						{"username": session.get("logged_in_user")},
						{"_id": 1}
					)["_id"]
				else:
					return dev_problem()
				# Check if user is in group
				in_group = COLLECTIONS[collection].find_one(
					{
						session.get("user_type").lower(): user_id,
						"group": ObjectId(id)
					},
					{"_id": 0, "group": 1}
				)
				if in_group != None:
					# Get student_data and staff_data
					students_data, staff_data = [], []
					students_data_raw = COLLECTIONS["studentsGroup"].find(
						{"group": result["_id"]}
					)
					for data in students_data_raw:
						students_data.append(
							COLLECTIONS["students"].find_one(
								{"_id": data["student"]},
								{"_id": 1, "username": 1, "name": 1}
						))
					staff_data_raw = COLLECTIONS["staffGroup"].find(
						{"group": result["_id"]}
					)
					for data in staff_data_raw:
						staff_data.append(
							COLLECTIONS["staff"].find_one(
								{"_id": data["staff"]},
								{"_id": 1, "username": 1, "alias": 1}
						))
					# Pass it into render template
					return render_template(
						"group-individual.html",
						logged_in_user=session.get("logged_in_user"),
						group_data=result,
						students_data=students_data,
						staff_data=staff_data,
						valid_user_type=(session["user_type"] == "STAFF")
					)
				else:
					return render_template(
						"404-depression.html",
						logged_in_user=session.get("logged_in_user"),
						error_text="You're not in that group buddy."
					)
			else:
				return render_template(
					"404-depression.html",
					logged_in_user=session.get("logged_in_user"),
					error_text="You likely used an invalid group id."
				)
		elif request.method == "POST":
			if "change-tags" in request.form:
				return redirect(
					url_for(
						"website.group_tags_modify",
						id=id,
						tags=request.form["tags"]
					),
					code=307
				)
			elif "add-students" in request.form:
				return redirect(
					url_for(
						"website.group_member_add_remove",
						id=id,
						add_or_remove="add",
						student_or_staff="student",
						username=request.form["username"]
					),
					code=307
				)
			elif "add-staff" in request.form:
				return redirect(
					url_for(
						"website.group_member_add_remove",
						id=id,
						add_or_remove="add",
						student_or_staff="staff",
						username=request.form["username"]
					),
					code=307
				)
			else:
				return redirect(url_for("website.individual_group"))
	return dev_problem()

@website.route("/group/<id>/<add_or_remove>/<student_or_staff>/<username>", methods=["POST"] )
def group_member_add_remove(id, add_or_remove, student_or_staff, username):
	'''
	This function either
		redirects the user from the add/remove member to/from group page to the login page if the user is not logged in,
		redirects the user to the individual group page if the user making the request is not a staff user or staff/student user has been successfully added/removed to/from the group,
		renders the 404 error page of the website if the user uses an invalid group id,
		renders the 404 error page of the website if the 'add_or_remove' parameter is not either 'add' or 'remove',
		renders the 404 error page of the website if the 'student_or_staff' parameter is not either 'student' or 'staff',
		renders the 404 error page of the website if the user uses an invalid username,
		renders the 404 error page of the website if the user tries to add an existing student group member to the group, or
		renders the 404 error page of the website if the user tries to add an existing staff group member to the group.
		
	This function is an extension of the individual_announcement() function, and is used to process any modifications that is made to the members of the group.


	Parameters:
		id (str): The id of the group the staff user is trying to edit.
		add_or_remove (str): The toggle to decide whether to add or remove a user.
		student_or_staff (str): The toggle to decide whether to modify a student or staff user.
		username (str): The username of the user that is being modified.

	Returns:
		flask.redirect: Redirects the user to the login page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (login())
		OR
		flask.redirect: Redirects the user to the individual group page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (individual_group())
				id (str): The id of the group to redirect to.
		OR
		flask.render_template: Renders the 404 error page that informs the user that they are trying to access a nonexistent group.
			filename (str): The file name of the html file to be rendered. (404-depression.html)
			logged_in_user (str): The username of the logged in user.
			error_text (str): The error text to be displayed to the user on the error page. ("You likely used an invalid group id.")
		OR
		flask.render_template: Renders the 404 error page that informs the user that the 'add_or_remove' parameter in the link is invalid.
			filename (str): The file name of the html file to be rendered. (404-depression.html)
			logged_in_user (str): The username of the logged in user.
			error_text (str): The error text to be displayed to the user on the error page. (f"The link given is invalid.\n'{add_or_remove}' should either be 'add' or 'remove'.")
		OR
		flask.render_template: Renders the 404 error page that informs the user that the 'student_or_staff' parameter in the link is invalid.
			filename (str): The file name of the html file to be rendered. (404-depression.html)
			logged_in_user (str): The username of the logged in user.
			error_text (str): The error text to be displayed to the user on the error page. (f"The link given is invalid.\n'{student_or_staff}' should either be 'student' or 'staff'.")
		OR
		flask.render_template: Renders the 404 error page that informs the user that they used an invalid username.
			filename (str): The file name of the html file to be rendered. (404-depression.html)
			logged_in_user (str): The username of the logged in user.
			error_text (str): The error text to be displayed to the user on the error page. ("You likely used an invalid username.")
		OR
		flask.render_template: Renders the 404 error page that informs the user that the student user that they are trying to add to the group is already in the group.
			filename (str): The file name of the html file to be rendered. (404-depression.html)
			logged_in_user (str): The username of the logged in user.
			error_text (str): The error text to be displayed to the user on the error page. (f"'{member_info['name']}' is already part of group '{group_name}'.")
		OR
		flask.render_template: Renders the 404 error page that informs the user that that the staff user that they are trying to add to the group is already in the group.
			filename (str): The file name of the html file to be rendered. (404-depression.html)
			logged_in_user (str): The username of the logged in user.
			error_text (str): The error text to be displayed to the user on the error page. (f"'{member_info['alias']}' is already part of group '{group_name}'.")
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if "logged_in_user" not in session:
		return redirect(url_for("website.login"))
	elif session["user_type"] != "STAFF":
		return redirect(url_for("website.individual_group", id=id))
	else:
		## Check validity of input parameters
		# Get group_name (and check if id is valid)
		result = COLLECTIONS["groups"].find_one(
			{"_id": ObjectId(id)}
		)
		if result != None:
			group_name = result["name"]
		else:
			return render_template(
				"404-depression.html",
				logged_in_user=session.get("logged_in_user"),
				error_text="You likely used an invalid group id."
			)
		# Pick whether to add or remove the user (check if add_or_remove is valid)
		if add_or_remove not in ["add", "remove"]:
			return render_template(
				"404-depression.html",
				logged_in_user=session.get("logged_in_user"),
				error_text=f"The link given is invalid.\n'{add_or_remove}' should either be 'add' or 'remove'."
			)
		# Pick whether to modify a student or staff user (check if student_or_staff is valid)
		if student_or_staff not in ["student", "staff"]:
			return render_template(
				"404-depression.html",
				logged_in_user=session.get("logged_in_user"),
				error_text=f"The link given is invalid.\n'{student_or_staff}' should either be 'student' or 'staff'."
			)
		# Get student/staff name, username and alias(for staff) (and check if username is valid)
		if student_or_staff == "student":
			member_info = COLLECTIONS["students"].find_one(
				{"username": username},
				{"username": 1, "name": 1}
			)
		elif student_or_staff == "staff":
			member_info = COLLECTIONS["staff"].find_one(
				{"username": username},
				{"username": 1, "name": 1, "alias": 1}
			)
			member_info['name'] = member_info['alias']
		else:
			return dev_problem()
		if member_info == None:
			return render_template(
				"404-depression.html",
				logged_in_user=session.get("logged_in_user"),
				error_text="You likely used an invalid username."
			)
		## Process requests
		if request.method == "POST":
			if (add_or_remove == "add") and (student_or_staff == "student"):
				query = {
					"student": ObjectId(str(member_info["_id"])),
					"group": ObjectId(id)
				}
				result = COLLECTIONS["studentsGroup"].find_one(query)
				if result == None:
					COLLECTIONS["studentsGroup"].insert_one(query)
				else:
					return render_template(
						"404-depression.html",
						logged_in_user=session.get("logged_in_user"),
						error_text=f"'{member_info['name']}' is already part of group '{group_name}'."
					)
			elif (add_or_remove == "add") and (student_or_staff == "staff"):
				query = {
					"staff": ObjectId(str(member_info["_id"])),
					"group": ObjectId(id)
				}
				result = COLLECTIONS["staffGroup"].find_one(query)
				if result == None:
					COLLECTIONS["staffGroup"].insert_one(query)
				else:
					return render_template(
						"404-depression.html",
						logged_in_user=session.get("logged_in_user"),
						error_text=f"'{member_info['alias']}' is already part of group '{group_name}'."
					)
			elif (add_or_remove == "remove") and (student_or_staff == "student"):
				COLLECTIONS["studentsGroup"].delete_one({
					"student": ObjectId(str(member_info["_id"])),
					"group": ObjectId(id)
				})
			elif (add_or_remove == "remove") and (student_or_staff == "staff"):
				COLLECTIONS["staffGroup"].delete_one({
					"staff": ObjectId(str(member_info["_id"])),
					"group": ObjectId(id)
				})
			COLLECTIONS["groups"].update_one(
				{"_id": ObjectId(id)},
				{"$set": {"dateUpdated": datetime.now()}}
			)
			return redirect(url_for("website.individual_group", id=id))
	return dev_problem()

@website.route("/group/<id>/modify_tags/<tags>", methods=["POST"])
def group_tags_modify(id, tags):
	'''
	This function either
		redirects the user from the modify group tags page to the login page if the user is not logged in or
		redirects the user from the modify group tags page to the individual group page if the user making the request is not a staff user or the group tags have been modified successfully.
	
	This function is an extension of the individual_announcement() function, and is used to process any modifications that is made to the group tags.

		
	Parameters:
		id (str): The id of the group the user is trying to modify the tags of.
		tags (str): The updated list of tags to replace the existing ones.

	Returns:
		flask.redirect: Redirects the user to the login page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (login())
		OR
		flask.redirect: Redirects the user to the individual group page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (individual_group())
				id (str): The id of the group to redirect to.
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if "logged_in_user" not in session:
		return redirect(url_for("website.login"))
	elif session["user_type"] != "STAFF":
		return redirect(url_for("website.individual_group", id=id))
	else:
		if request.method == "POST":
			COLLECTIONS["groups"].update_one(
				{"_id": ObjectId(id)},
				{"$set": {"tags": tags.split("\n")}}
			)
			return redirect(url_for("website.individual_group", id=id))
	return dev_problem()

@website.route("/group/create", methods=["GET", "POST"])
def create_group():
	'''
	This function either
		redirects the user from the create group page to the login page if the user is not logged in,
		redirects the user from the create group page to the general groups page if the user making the request is not a staff user or the group has been successfully created, or
		renders the create group page if the user is logged in.
	
	This function is an extension of the groups() function, and is used to create new groups.

		
	Parameters:
		NIL

	Returns:
		flask.redirect: Redirects the user to the login page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (login())
		OR
		flask.redirect: Redirects the user to the general groups page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (groups())
		OR
		flask.render_template: Renders the create group page.
			filename (str): The file name of the html file to be rendered. (group-create.html)
			logged_in_user (str): The username of the logged in user.
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if "logged_in_user" not in session:
		return redirect(url_for("website.login"))
	elif session["user_type"] != "STAFF":
		return redirect(url_for("website.groups"))
	else:
		if request.method == "GET":
			return render_template(
				"group-create.html",
				logged_in_user=session.get("logged_in_user")
			)
		elif request.method == "POST":
			document = COLLECTIONS["groups"].insert_one({
				"name": request.form["name"],
				"tags": request.form["tags"].split("\n"),
				"dateUpdated": datetime.now()
			})
			result = COLLECTIONS["staff"].find_one(
				{"username": session.get("logged_in_user")},
				{"_id": 1}
			)
			COLLECTIONS["staffGroup"].insert_one({
				"staff": result["_id"],
				"group": ObjectId(str(document.inserted_id))
			})
			return redirect(url_for("website.groups"))
	return dev_problem()

@website.route("/group/<id>/delete", methods=["GET", "POST"])
def delete_group(id):
	'''
	This function either
		redirects the user from the delete group page to the login page if the user is not logged in,
		redirects the user from the delete group page to the individual group page if the user making the request is not a staff user,
		renders the delete group page if the user is logged in,
		redirects the user from the delete group page to the general groups page if the group was deleted successfully.
	
	This function is an extension of the individual_announcement() function, and is used to delete groups.
	

	Parameters:
		id (str): The id of the group the user is trying to delete.

	Returns:
		flask.redirect: Redirects the user to the login page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (login())
		OR
		flask.redirect: Redirects the user to the individual group page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (individual_group())
				id (str): The id of the group to redirect to.
		OR
		flask.render_template: Renders the delete group page.
			filename (str): The file name of the html file to be rendered. (group-delete.html)
			logged_in_user (str): The username of the logged in user.
		OR
		flask.redirect: Redirects the user to the general groups page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (groups())
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if "logged_in_user" not in session:
		return redirect(url_for("website.login"))
	elif session["user_type"] != "STAFF":
		return redirect(url_for("website.individual_group", id=id))
	else:
		if request.method == "GET":
			return render_template(
				"group-delete.html",
				logged_in_user=session.get("logged_in_user")
			)
		elif request.method == "POST":
			COLLECTIONS["groups"].delete_one(
				{"_id": ObjectId(id)}
			)
			COLLECTIONS["studentsGroup"].delete_many(
				{"group": ObjectId(id)}
			)
			COLLECTIONS["staffGroup"].delete_many(
				{"group": ObjectId(id)}
			)
			return redirect(url_for("website.groups"))
	return dev_problem()


# Notifications
@website.route("/notifications", methods=["GET"])
def notifications():
	'''
	This function either
		redirects the user from the notifications page to the login page if the user is not logged in or
		renders the notificatins page if the user is logged in.
	
	This function shows the users notifications about anything on the website that requires their attention. For now, it only shows the announcements that they have not marked as read, but we plan to add in more types of notifications, for example when the user is added/removed from a group, in future updates (should there be any).

		
	Parameters:
		NIL

	Returns:
		flask.redirect: Redirects the user to the login page.
			flask.url_for: Gets the url to redirect the user to.
				function (str): The function that should be triggered when redirecting. (login())
		OR
		flask.render_template: Renders the create group page.
			filename (str): The file name of the html file to be rendered. (notifications.html)
			logged_in_user (str): The username of the logged in user.
			notifs (): The notificatins to be showed to the user
		OR
		dev_problem(): A function that triggers only if the developers have made a mistake in the code.
	'''
	if "logged_in_user" not in session:
		return redirect(url_for("website.login"))
	else:
		if request.method == "GET":
			# Pages Setup (10 Announcements per page)
			options = dict(request.args)
			if "page" not in options.keys():
				page = 0
				displayed_page = 0
			else:
				page = int(options["page"])
				displayed_page = page
				if page < 0:
					page = 0
			# Get user_id and collection
			if session["user_type"] == "STUDENT":
				collection = "studentsGroup"
				user_id = COLLECTIONS["students"].find_one(
					{"username": session.get("logged_in_user")},
					{"_id": 1}
				)["_id"]
			elif session["user_type"] == "STAFF":
				collection = "staffGroup"
				user_id = COLLECTIONS["staff"].find_one(
					{"username": session.get("logged_in_user")},
					{"_id": 1}
				)["_id"]
			else:
				return dev_problem()
			# Get list of groups user is in
			in_group = COLLECTIONS[collection].find(
				{session.get("user_type").lower(): user_id},
				{"_id": 0, "group": 1}
			)
			group_list = [None]
			for group in in_group:
				group_list.append(group["group"])
			announcements = list(
				COLLECTIONS["forms"].find({
					"type": "announcement",
					"targetGroup": {"$in": group_list}
				}).sort("_id", -1)
			)
			for announcement in announcements:
				announcement["datePosted"] = aware_datetime(announcement["datePosted"])
			user_id = ObjectId(user_id)
			new_announcements = []
			# Check which announcements have been read
			# If not read, add to new_announcements
			for announcement in announcements:
				already_read = False
				for reader in announcement["bluetick"]:
					if user_id == reader["reader"]:
						already_read = True
						break
				if not already_read:
					new_announcements.append(
						{
							"notif": announcement,
							"notif_type": "announcement"
						}
					)
			return render_template(
				"notifications.html",
				logged_in_user=session.get("logged_in_user"),
				notifs=new_announcements
			)
	return dev_problem()