from flask import Flask, render_template, request

from estimator import (
    async_estimator,  # This is a hypothetical async version of your estimator function
)

app = Flask(__name__)


@app.route("/")
async def index():
    return render_template("index.html")


@app.route("/calculate")
async def calculate():
    url = request.args.get("url")
    if url is None or url == "":
        return "No URL provided"

    try:
        result = await async_estimator(url, verbose=True)  # This assumes estimator is also async
    except Exception as exc_info:
        print(str(exc_info))
        result = "Something went wrong. :-( Please try again."

    return result


if __name__ == "__main__":
    app.run(debug=True)
