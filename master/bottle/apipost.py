## Import dependencies
# Import external modules
from flask import Blueprint, request, redirect, Response
from bson.json_util import loads, dumps

# Import own modules
from ..mongosetup import *


## API setup
# Initialise app
apipost = Blueprint("apipost", __name__)

# Template
template = {"status": {"success": True, "code": 200},"data": {}}

# General route to POST API
def rt(route):
	return "/api/post/"+route+"/"
	
'''
def procform(delivery):
	obj = {}
	try:
		obj = loads(list(delivery.keys())[0])
	except:
		pass
	else:
		print("1")
		return obj
	try:
		obj = delivery.to_dict()
	except:
		pass
	else:
		print("2")
		return obj
	return obj
'''

## POST Functions
# Students
@apipost.route(rt("student"), methods=["POST"])
def post_student():
	data = template
	delivery = request.get_json(force=True)
	data["data"]["received"] = delivery
	return Response(
		dumps(data), status=200, mimetype="application/json"
	)