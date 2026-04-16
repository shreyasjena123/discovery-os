import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "workflows"))

from flask import Flask, jsonify, request
from flask_cors import CORS

from process_signals_api import run_api, run_stage2_api

app = Flask(__name__, static_folder=".")
CORS(app)


@app.route("/")
def index():
    try:
        with open("index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "index.html not found", 404


@app.route("/api/analyze", methods=["POST"])
def analyze():
    api_key = request.headers.get("X-API-Key", "")
    data = request.get_json(force=True) or {}
    result = run_api(
        signals=data.get("signals", ""),
        context=data.get("context", {}),
        api_key=api_key,
    )
    return jsonify({"success": result["error"] is None, **result})


@app.route("/api/experiments", methods=["POST"])
def experiments():
    api_key = request.headers.get("X-API-Key", "")
    data = request.get_json(force=True) or {}
    result = run_stage2_api(
        stage1_output=data.get("stage1_output", ""),
        selected_hypotheses=data.get("selected_hypotheses", []),
        constraints=data.get("constraints", ""),
        api_key=api_key,
    )
    return jsonify({"success": result["error"] is None, **result})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
