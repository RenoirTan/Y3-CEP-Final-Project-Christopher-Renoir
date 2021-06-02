from waitress import serve
from master import app

PORT: int = 5000
HOST: str = "0.0.0.0"


def launch():
    serve(app, host=HOST, port=PORT)


if __name__ == "__main__":
    launch()
