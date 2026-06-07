from flask import Flask, jsonify, logging, request
from flask_caching import Cache
import time
import random
import logging

app = Flask(__name__)
app.config.from_object("config.Config")

cache = Cache(app)

logging.basicConfig(level=logging.INFO)

@app.route("/")
def home():
  app.logger.info("Home endpoint hit")
  return jsonify({"message": "Hello from flask App!"})


@app.route("/health")
def health():
  return jsonify({"status": "OK"}), 200

@app.route("/heavy")
def heavy():
  app.logger.info("Heavy endpoint simulateing load")
  time.sleep(65)  # Simulate a heavy operation
  return jsonify({"message": "Heavy Configuration done!"})

@app.route("/cacheme/<param>")
@cache.cached(timeout=30)  # Cache for 30 seconds
def cacheme(param):
  app.logger.info(f"Cache result for:: {param}")
  return jsonify({"message": f"Hello, {param}!"}, random=random.randint(1, 1000))  # Include timestamp to show caching effect


@app.route("/error")
def error():
  app.logger.error("Intentional error endpoint triggered")
  raise Exception("This is a test error for minitoring/logging purposes")

@app.errorhandler(Exception)
def handle_exception(e):
  app.logger.error("Unhandeled exception: %s", str(e))
  return jsonify({"error": "An internal error occurred", "message": str(e)}), 500

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=5000)