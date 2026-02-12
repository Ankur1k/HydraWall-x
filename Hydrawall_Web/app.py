from flask import Flask, render_template, jsonify
import pandas as pd
import joblib
import os
import subprocess
import time

app = Flask(__name__)

# --- CONFIGURATION ---
MODEL_FILE = 'hydrawall_model.pkl'
DATA_FILE = 'system_data_cleaned.csv'
# Paths for the SSL certificates you just generated
CERT_FILE = 'localhost.pem'
KEY_FILE = 'localhost-key.pem'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    try:
        # 1. Check if threat data exists
        if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size <= 10:
            return jsonify({"status": "Success", "health": 100, "threat_count": 0})

        # 2. Load the injected data
        df = pd.read_csv(DATA_FILE)
        if df.empty:
             return jsonify({"status": "Success", "health": 100, "threat_count": 0})
             
        # 3. Load AI Model and Predict
        # If the model file is missing, we'll return a simulation health of 100
        if not os.path.exists(MODEL_FILE):
            return jsonify({"status": "Error", "message": "AI Model not found"})

        model = joblib.load(MODEL_FILE)
        predictions = model.predict(df[['PID', 'PPID']])
        
        # Isolation Forest returns -1 for outliers (threats)
        threat_indices = (predictions == -1)
        threat_count = int(threat_indices.sum())
        
        if threat_count > 0:
            # Calculate health drop (e.g., each threat removes 20%)
            health = max(0, 100 - (threat_count * 20))
            
            # 4. MITRIGATION: Neutralize the PIDs
            bad_pids = df[threat_indices]['PID'].unique()
            for pid in bad_pids:
                try:
                    # Simulation: In a real environment, this kills the malicious process
                    subprocess.run(['kill', '-9', str(int(pid))], check=False)
                    print(f"🛡️  HYDRAWALL-X: Terminated malicious PID {pid}")
                except Exception as e:
                    print(f"⚠️  Failed to kill {pid}: {e}")

            # 5. SELF-HEALING: Clear the CSV after detection so health returns to 100%
            # We wait 3 seconds so the user can actually see the "Red" state on the dashboard
            time.sleep(1) 
            with open(DATA_FILE, 'w') as f:
                f.write("PID,PPID\n")
            
            return jsonify({
                "status": "Success",
                "health": health,
                "threat_count": threat_count
            })

        return jsonify({"status": "Success", "health": 100, "threat_count": 0})

    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)})

if __name__ == '__main__':
    # Check if SSL certificates exist before starting
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        print("🔒 Starting Secure Server (HTTPS)")
        app.run(
            debug=True, 
            host='0.0.0.0', 
            port=5000, 
            ssl_context=(CERT_FILE, KEY_FILE)
        )
    else:
        print("⚠️  SSL Certificates not found! Falling back to HTTP.")
        app.run(debug=True, host='0.0.0.0', port=5000)
