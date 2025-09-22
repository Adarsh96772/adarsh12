from flask import Flask, render_template, request, jsonify
import os
import json
import webbrowser
from threading import Timer

app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/metrics")
def get_metrics():
    mode = request.args.get("mode", "forking").lower()

    live_file = f"live_{mode}_metrics.json"
    fallback_file = f"{mode}_simulation_results.json"
    selected_file = live_file if os.path.exists(live_file) else fallback_file

    if not os.path.exists(selected_file):
        print(f"[WARN] Metrics file not found for mode: {mode}")
        return jsonify({
            "throughput": 0.0,
            "clients_served": 0,
            "lost_clients": 0,
            "avg_rating": 0.0,
            "utilization": 0.0
        })

    try:
        with open(selected_file, "r") as f:
            data = json.load(f)

        # Extract metrics
        metrics = data.get("metrics", data)  # fallback to flat if no "metrics" key

        response = {
            "throughput": float(metrics.get("throughput", 0.0)),
            "clients_served": int(metrics.get("total_clients_served", 0)),
            "lost_clients": int(metrics.get("total_lost_clients", 0)),
            "avg_rating": float(metrics.get("average_rating", 0.0)),
            "utilization": float(metrics.get("server_utilization", 0.0))
        }

        print(f"[INFO] {mode.capitalize()} → {response}")
        return jsonify(response)

    except Exception as e:
        print(f"[ERROR] Failed to read {selected_file}: {e}")
        return jsonify({
            "throughput": 0.0,
            "clients_served": 0,
            "lost_clients": 0,
            "avg_rating": 0.0,
            "utilization": 0.0
        })


def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    print("[INFO] Starting Flask dashboard server...")
    Timer(1.5, open_browser).start()
    app.run(debug=True)