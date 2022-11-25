import sys

sys.path.append(".")  # so submodules can import app

from waitress import serve
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/api/user/<id>")
def get_user(id):
    users = [
        {"email": "john.doe@example.com", "id": "1", "name": "John Doe"},
        {"email": "karel.novak@example.com", "id": "2", "name": "Karel Novak"},
    ]

    for user in users:
        if user["id"] == id:
            return jsonify(user)

    return jsonify({}), 404


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)
