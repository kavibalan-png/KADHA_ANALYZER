from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
import os
import csv
import socket
from sklearn.ensemble import RandomForestClassifier
from zeroconf import Zeroconf, ServiceInfo

app = Flask(__name__)

# ---------------- GLOBAL STORAGE ----------------
latest_sensor = {}
temp_sample = {}

DATA_FILE = "data/herb_data.csv"
MODEL_DIR = "model"

# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------- COLLECT PAGE ----------------
@app.route("/collect")
def collect():
    return render_template("collect.html")

# ---------------- PREDICT PAGE ----------------
@app.route("/predict")
def predict():
    return render_template("predict.html")

# ---------------- TRAIN PAGE ----------------
@app.route("/train")
def train():
    return render_template("train.html")

# =================================================
# ✅ ESP32 → FLASK DATA RECEIVER
# =================================================
@app.route("/esp32/data", methods=["POST"])
def esp32_data():
    global latest_sensor

    data = request.get_json(force=True)

    if not data:
        return jsonify({"status": "error", "message": "No JSON received"}), 400

    latest_sensor = data
    print("📥 ESP32 DATA RECEIVED:", latest_sensor)

    return jsonify({"status": "ok"}), 200

# =================================================
# ✅ FETCH SENSOR
# =================================================
@app.route("/get/<sensor>")
def get_sensor(sensor):
    if not latest_sensor:
        return jsonify({"error": "No data available from ESP32"}), 400

    if sensor not in latest_sensor:
        return jsonify({"error": f"{sensor} not found"}), 400

    temp_sample[sensor] = latest_sensor[sensor]
    return jsonify({"value": latest_sensor[sensor]}), 200

# =================================================
# ✅ SAVE DATA
# =================================================
@app.route("/finish", methods=["POST"])
def finish():
    d = request.json
    os.makedirs("data", exist_ok=True)

    file_exists = os.path.isfile(DATA_FILE)

    with open(DATA_FILE, "a", newline="") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(["herb", "purity", "ph", "tds", "optical"])

        w.writerow([
            d["herb"],
            d["purity"],
            d["ph"],
            d["tds"],
            d["optical"]
        ])

    temp_sample.clear()
    return jsonify({"status": "saved"}), 200

# =================================================
# ✅ TRAIN MODEL
# =================================================
@app.route("/make_model", methods=["POST"])
def make_model():
    if not os.path.exists(DATA_FILE):
        return jsonify({"error": "No data collected yet"}), 400

    df = pd.read_csv(DATA_FILE)
    if df.empty:
        return jsonify({"error": "CSV empty"}), 400

    X = df[["ph", "tds", "optical"]]
    herb_y = df["herb"]
    purity_y = df["purity"]

    herb_model = RandomForestClassifier(n_estimators=200)
    purity_model = RandomForestClassifier(n_estimators=200)

    herb_model.fit(X, herb_y)
    purity_model.fit(X, purity_y)

    os.makedirs(MODEL_DIR, exist_ok=True)

    joblib.dump(herb_model, f"{MODEL_DIR}/taste_model.pkl")
    joblib.dump(purity_model, f"{MODEL_DIR}/purity_model.pkl")

    return jsonify({"status": "model trained"}), 200

# =================================================
# ✅ PREDICT
# =================================================
@app.route("/predict_result", methods=["POST"])
def predict_result():
    if not os.path.exists(f"{MODEL_DIR}/taste_model.pkl"):
        return jsonify({"error": "Model not trained"}), 400

    data = request.json
    X = [[data["ph"], data["tds"], data["optical"]]]

    herb_model = joblib.load(f"{MODEL_DIR}/taste_model.pkl")
    purity_model = joblib.load(f"{MODEL_DIR}/purity_model.pkl")

    herb = herb_model.predict(X)[0]
    purity = purity_model.predict(X)[0]

    herb_conf = max(herb_model.predict_proba(X)[0]) * 100
    purity_conf = max(purity_model.predict_proba(X)[0]) * 100

    return jsonify({
        "herb": herb,
        "purity": purity,
        "confidence": round((herb_conf + purity_conf) / 2, 2)
    }), 200

# =================================================
# ✅ AUTO IP + mDNS (PLUG & PLAY)
# =================================================
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

if __name__ == "__main__":
    ip = get_local_ip()

    zeroconf = Zeroconf()
    service_info = ServiceInfo(
        "_http._tcp.local.",
        "herb._http._tcp.local.",
        addresses=[socket.inet_aton(ip)],
        port=5000,
        properties={},
        server="herb.local."
    )

    zeroconf.register_service(service_info)

    print("🌿 Herbal E-Tongue Server Running")
    print(f"🌐 Open: http://herb.local:5000")

    app.run(host="0.0.0.0", port=5000, debug=True)
