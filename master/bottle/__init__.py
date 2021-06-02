## Import dependencies
# Import flask
from flask import Flask

# Import own modules
from .apiget import apiget
from .apipost import apipost
from .website import website

## Flask setup
app = Flask(
	__name__,
	static_url_path="",
	static_folder="../../static"
)
app.secret_key = "2387r324rgtf4783wtfghw8fhef89whfwfgtnw4i"
app.register_blueprint(apiget)
app.register_blueprint(apipost)
app.register_blueprint(website)

# Change host="0.0.0.0" to host="127.0.0.1" if running on local compile
# host="0.0.0.0" is for it to run on repl.it
def run(host="0.0.0.0", port=5000, debug=True):
	global app
	print("RUNNING")
	app.run(host=host, port=port, debug=debug)
	print("KILLED")
