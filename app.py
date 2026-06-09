from flask import Flask, jsonify, logging, request
from flask_caching import Cache
import time
import random
import logging
import os
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


app = Flask(__name__)
app.config.from_object("config.Config")

Compress(app)

cache = Cache(app)
limiter = Limiter(get_remote_address, app=app)

logging.basicConfig(level=logging.INFO)

@app.route("/")
def home():
  app.logger.info("Home endpoint hit")
  return jsonify({"message": "Hello from flask App v4!"})


@app.route("/health")
def health():
  return jsonify({"status": "OK"}), 200

@app.route("/heavy")
def heavy():
  app.logger.info("Heavy endpoint simulating load")
  time.sleep(65)  # Simulate a heavy operation
  return jsonify({"message": "Heavy Configuration done!"})

@app.route("/cacheme/<param>")
@cache.cached(timeout=30)  # Cache for 30 seconds
def cacheme(param):
  app.logger.info(f"Cache result for:: {param}")
  return jsonify({"message": f"Hello, {param}!", "random": random.randint(1, 1000)})  # Include timestamp to show caching effect


@app.route("/error")
def error():
  app.logger.error("Intentional error endpoint triggered")
  raise Exception("This is a test error for monitoring/logging purposes")

@app.errorhandler(Exception)
def handle_exception(e):
  app.logger.error("Unhandled exception: %s", str(e))
  return jsonify({"error": "An internal error occurred", "message": str(e)}), 500

@app.route("/bigjson")
def bigjson():
  app.logger.info("Big JSON endpoint hit")
  big_data = {"data": [f"Item {i}" for i in range(1000)]}  # Simulate a large JSON response
  return jsonify(big_data)

@app.route("/api")
@limiter.limit("5/minute")  # Limit to 5 requests per minute
def api():
  worker = os.getpid()
  app.logger.info(f"API endpoint hit by worker {worker}")
  return jsonify({"message": "This is a rate-limited API endpoint", "worker": worker})

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=5000)