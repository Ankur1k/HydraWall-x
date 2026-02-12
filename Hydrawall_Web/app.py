from flask import Flask, render_template_string, jsonify
import pandas as pd
import joblib
import os
import time

app = Flask(__name__)

# --- CONFIGURATION ---
DATA_FILE = 'system_data_cleaned.csv'
MODEL_FILE = 'hydrawall_model.pkl'

# --- ENCRYPTED HUD UI ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>HYDRAWALL-X | ENCRYPTED HUD</title>
    <style>
        :root { --neon-green: #00ff41; --neon-red: #ff3131; --bg-black: #050505; }
        body { background-color: var(--bg-black); color: var(--neon-green); font-family: 'Courier New', monospace; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .main-frame { border: 2px solid var(--neon-green); box-shadow: 0 0 20px var(--neon-green); background: rgba(0, 15, 0, 0.9); width: 90%; max-width: 1000px; padding: 30px; position: relative; }
        .threat-alert { border-color: var(--neon-red) !important; box-shadow: 0 0 50px var(--neon-red) !important; color: var(--neon-red) !important; }
        .grid { display: grid; grid-template-columns: 1fr 1.5fr; gap: 20px; }
        .stat-card { border: 1px solid var(--neon-green); padding: 15px; background: rgba(0,0,0,0.7); text-align: center; }
        .radar-circle { width: 80px; height: 80px; border-radius: 50%; border: 2px solid var(--neon-green); margin: 20px auto; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { transform: scale(0.9); opacity: 1; } 70% { transform: scale(1.1); opacity: 0.3; } 100% { transform: scale(0.9); opacity: 1; } }
        .red-pulse { border-color: var(--neon-red) !important; animation: pulse-red 0.5s infinite !important; }
        @keyframes pulse-red { 50% { box-shadow: 0 0 20px var(--neon-red); } }
        #terminal { height: 180px; background: black; border: 1px solid #222; font-size: 0.8rem; padding: 10px; overflow-y: hidden; display: flex; flex-direction: column-reverse; color: #00ff41; }
        .security-badge { position: absolute; top: 10px; right: 10px; font-size: 0.7rem; border: 1px solid var(--neon-green); padding: 2px 5px; }
    </style>
</head>
<body>
<div class="main-frame" id="main-frame">
    <div class="security-badge">[ SSL_ENCRYPTED_NODE ]</div>
    <div style="text-align:center; border-bottom:1px solid var(--neon-green); margin-bottom:20px; padding-bottom:10px;">
        <h1>HYDRAWALL-X SENTINEL</h1>
    </div>
    <div class="grid">
        <div class="left-panel">
            <div class="stat-card">
                <div>AI KERNEL SCANNER</div>
                <div id="radar" class="radar-circle"></div>
                <div id="status-text">ENCRYPTED FEED</div>
            </div>
            <div class="stat-card" style="margin-top:20px;">
                HEALTH: <span id="health-val">100%</span>
                <div style="width:100%; height:10px; background:#111; border:1px solid var(--neon-green); margin-top:5px;">
                    <div id="health-bar" style="height:100%; background:var(--neon-green); width:100%; transition: 0.5s;"></div>
                </div>
            </div>
        </div>
        <div class="right-panel">
            <div class="stat-card">
                DETECTIONS: <span id="threat-val" style="font-size:2.5rem;">0</span>
            </div>
            <div id="terminal" style="margin-top:20px;"></div>
        </div>
    </div>
</div>
<script>
    async function update() {
        try {
            const res = await fetch('/api/stats');
            const data = await res.json();
            document.getElementById('health-val').innerText = data.health + "%";
            document.getElementById('threat-val').innerText = data.threat_count;
            document.getElementById('health-bar').style.width = data.health + "%";
            
            const frame = document.getElementById('main-frame');
            const radar = document.getElementById('radar');
            const term = document.getElementById('terminal');
            const line = document.createElement('div');
            
            if (data.threat_count > 0) {
                frame.classList.add('threat-alert');
                radar.classList.add('red-pulse');
                line.innerHTML = `<span style="color:red;">> [${new Date().toLocaleTimeString()}] ALERT: MALICIOUS PID INJECTION DETECTED</span>`;
            } else {
                frame.classList.remove('threat-alert');
                radar.classList.remove('red-pulse');
                line.innerHTML = `> [${new Date().toLocaleTimeString()}] Secure telemetry packet received.`;
            }
            term.prepend(line);
            if(term.childNodes.length > 8) term.removeChild(term.lastChild);
        } catch (e) { console.log("SSL handshake error or connection lost."); }
    }
    setInterval(update, 1000);
</script>
</body>
</html>
"""

@app.route('/api/stats')
def get_stats():
    health, threat_count = 100, 0
    try:
        if os.path.exists(DATA_FILE) and os.stat(DATA_FILE).st_size > 15:
            df = pd.read_csv(DATA_FILE)
            if os.path.exists(MODEL_FILE):
                model = joblib.load(MODEL_FILE)
                predictions = model.predict(df[['PID', 'PPID']])
                threat_count = int((predictions == -1).sum())
                if threat_count > 0:
                    health = 30
                    time.sleep(2) # Visual pause
                    with open(DATA_FILE, 'w') as f: f.write("PID,PPID\n")
        return jsonify({"health": health, "threat_count": threat_count})
    except:
        return jsonify({"health": 100, "threat_count": 0})

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    # Using local SSL certs for HTTPS
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))
