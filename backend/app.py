from logger import save_prompt_log, get_all_logs
from ai_analyzer import analyze_with_claude
from scraper import scrape_page
from flask_cors import CORS
from flask import Flask, request, jsonify
from datetime import datetime
import uuid
import time
import json
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
CORS(app)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/audit", methods=["POST"])
def audit():
    data = request.get_json()
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"error": "URL is required"}), 400

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Step 1: Scrape
    try:
        metrics, page_text = scrape_page(url)
    except Exception as e:
        return jsonify({"error": f"Failed to scrape URL: {str(e)}"}), 422

    # Step 2: AI Analysis
    try:
        ai_result, prompt_log = analyze_with_claude(url, metrics, page_text)
    except Exception as e:
        return jsonify({"error": f"AI analysis failed: {str(e)}"}), 500

    # Step 3: Save prompt log
    log_id = str(uuid.uuid4())[:8]
    save_prompt_log(log_id, url, prompt_log)

    return jsonify({
        "url": url,
        "log_id": log_id,
        "metrics": metrics,
        "insights": ai_result.get("insights", {}),
        "recommendations": ai_result.get("recommendations", []),
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/logs", methods=["GET"])
def logs():
    return jsonify(get_all_logs())


@app.route("/logs/<log_id>", methods=["GET"])
def get_log(log_id):
    all_logs = get_all_logs()
    log = next((l for l in all_logs if l["log_id"] == log_id), None)
    if not log:
        return jsonify({"error": "Log not found"}), 404
    return jsonify(log)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
