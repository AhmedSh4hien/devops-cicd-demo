import os
from flask import Flask, jsonify

app = Flask(__name__)
VERSION = os.getenv("APP_VERSION", "dev")


@app.route("/")
def index():
    return jsonify(message="Hello from the demo app", version=VERSION)


@app.route("/health")
def health():
    return jsonify(status="ok"), 200