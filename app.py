import requests
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate")
def calculate():
    url = request.args.get("url")
    response = requests.get(f"http://127.0.0.1:8000/predict?url={url}")
    return response.text


if __name__ == "__main__":
    app.run(debug=True)
