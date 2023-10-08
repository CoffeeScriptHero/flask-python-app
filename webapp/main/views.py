from flask import jsonify, render_template
from webapp import app
from datetime import datetime, timedelta


@app.route("/", methods=["GET"])
def base_url():
    return render_template("index.html")


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    ua_current_time = datetime.utcnow() + timedelta(hours=3)
    formatted_time = ua_current_time.strftime("%Y-%m-%d %H:%M:%S")
    response = {
        "status": "OK",
        "current_time": formatted_time
    }
    return jsonify(response), 200
