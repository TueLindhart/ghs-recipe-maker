from flask import Flask, render_template, request

from estimator import estimator

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate")
def calculate():
    url = request.args.get("url")
    if url is None or url == "":
        return "No URL provided"

    try:
        result = estimator(url, verbose=True)
    except Exception:
        result = "Something went wrong. :-( Please try again."

    return result


if __name__ == "__main__":
    app.run(debug=True)
