## Import dependencies
# Import external modules
from flask import Blueprint, request, redirect, Response
from bson.json_util import loads, dumps

# Import own modules
from ..mongosetup import *


## API setup
# Initialise app
apiget = Blueprint("apiget", __name__)

# Template
template = {"status": {"success": True, "code": 200},"data": {}}

# General route to GET API
def rt(route):
	return "/api/get/"+route+"/"

# For testing
@apiget.route(rt("debug"), methods=["GET"])
def get_debug():
	data = template
	query = mongos_get_students(dict(request.args))
	data["data"]["returns"] = query
	return Response(
		dumps(data), status=200, mimetype="application/json"
	)


## GET Functions
# Students
@apiget.route(rt("student"), methods=["GET"])
def get_student():
	data = template
	query = process_request(
		query=dict(request.args),
		regex_attributes=[
			"username",
			"name"
		]
	)
	data["data"]["returns"] = COLLECTIONS["students"].find(*query)
	return Response(
		dumps(data), status=200, mimetype="application/json"
	)

# Parents
@apiget.route(rt("parent"),methods=["GET"])
def get_parent():
	data = template
	query = process_request(
		query=dict(request.args),
		regex_attributes=[
			"username",
			"prefix",
			"name",
			"alias",
			"type"
		]
	)
	data["data"]["returns"] = COLLECTIONS["parents"].find(*query)
	return Response(
		dumps(data), status=200, mimetype="application/json"
	)

# Staff
@apiget.route(rt("staff"),methods=["GET"])
def get_staff():
	data = template
	query = process_request(
		query=dict(request.args),
		regex_attributes=[
			"username",
			"prefix",
			"name",
			"alias",
		]
	)
	data["data"]["returns"] = COLLECTIONS["staff"].find(*query)
	return Response(
		dumps(data), status=200, mimetype="application/json"
	)

# Groups
@apiget.route(rt("groups"),methods=["GET"])
def get_groups():
	data = template
	query = process_request(
		query=dict(request.args),
		regex_attributes=[
			"name"
		]
	)
	data["data"]["returns"] = COLLECTIONS["groups"].find(*query)
	return Response(
		dumps(data), status=200, mimetype="application/json"
	)

# Error 404
@apiget.route("/404")
def redirect404():
	data = template
	data["status"] = {"success": False, "code": 404}
	Response(
		dumps(data), status=404, mimetype="application/json"
	)

## Error Handling
# Handle error 404
@apiget.errorhandler(404)
def error404(error):
	return redirect("/404", code=404)