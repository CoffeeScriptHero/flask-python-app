from flask import jsonify, render_template
from webapp import app
from datetime import datetime


@app.route("/", methods=["GET"])
def base_url():
    return render_template("index.html")


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    response = {
        "status": "OK",
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return jsonify(response), 200
