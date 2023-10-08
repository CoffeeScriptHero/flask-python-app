from main import app


@app.route("/")
def healthcheck():
    return ("<div>"
            "<p style=\"color:#946aa5\">Hello, World!</p>"
            "<p style=\"color:#0067b1\">First lab © Denys Kozarenko IO-13</p>"
            "</div>")
