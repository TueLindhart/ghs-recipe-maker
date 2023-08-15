import asyncio
import hashlib
import threading

from flask import Flask, jsonify, render_template, request

from estimator import async_estimator

app = Flask(__name__)

results = {}  # Temporary storage for results


def hash_url(url):
    """Generate a short hash from a URL."""
    return hashlib.md5(url.encode()).hexdigest()


def run_in_thread(func, url):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    hashed_url = hash_url(url)
    try:
        result = loop.run_until_complete(func(url, verbose=True))
        results[hashed_url] = result
    except Exception as exc_info:
        print(str(exc_info))
        results[hashed_url] = "Something went wrong. :-( Please try again."
    finally:
        loop.close()


@app.route("/")
async def index():
    return render_template("index.html")


@app.route("/calculate")
async def calculate():
    url = request.args.get("url")
    if url is None or url == "":
        return "No URL provided"

    threading.Thread(target=run_in_thread, args=(async_estimator, url)).start()

    return jsonify(status="Processing", url=url), 202  # Return 202 Accepted status


@app.route("/results/<hashed_url>")
async def get_results(hashed_url):
    result = results.get(hashed_url, None)
    if result:
        return jsonify(status="Completed", result=result), 200  # Return as a JSON object
    else:
        return jsonify(status="Processing", url=hashed_url), 202  # Maintain consistency with a JSON response


if __name__ == "__main__":
    app.run(debug=True, port=8000)
