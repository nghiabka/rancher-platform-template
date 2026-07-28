from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def index():
    return jsonify({"service": "sample-api", "status": "ok"})


@app.get("/healthz")
def healthz():
    return jsonify({"status": "healthy"})


@app.get("/metrics")
def metrics():
    return "sample_api_requests_total 1\n", 200, {"Content-Type": "text/plain"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
