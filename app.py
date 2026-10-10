from flask import Flask, request, jsonify, Response
from datetime import datetime

app = Flask(__name__)

# Single bin data
sensor_data = {
    "volume": 0.0,
    "last_updated": None,
    "lid_status": "closed"
}

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<title>SmartBin Monitor</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700;900&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #121212;
  --card: #1e1e1e;
  --text-main: #f0f0f0;
  --text-muted: #a0a0a0;
  --accent: #facc15; /* Duck yellow */
  --accent-glow: rgba(250, 204, 21, 0.4);
}
* { margin:0; padding:0; box-sizing:border-box; }
body { background: var(--bg); color: var(--text-main); font-family: 'Outfit', sans-serif; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; overflow-x: hidden; }

/* Background styling */
.bg-gradient { position: fixed; inset: 0; z-index: -1; background: radial-gradient(circle at 50% -20%, #2a2a2a, var(--bg) 70%); }

.app-container { width: 100%; max-width: 500px; display: flex; flex-direction: column; gap: 30px; }

/* Header */
.header { text-align: center; }
.header h1 { font-size: 2.2rem; font-weight: 900; letter-spacing: 2px; text-transform: uppercase; color: #fff; text-shadow: 0 4px 20px rgba(255,255,255,0.1); }
.header p { color: var(--text-muted); font-size: 0.95rem; margin-top: 5px; font-weight: 300; }

/* Main Card */
.card { background: var(--card); border-radius: 24px; padding: 30px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.05); position: relative; overflow: hidden; display: flex; flex-direction: column; align-items: center; gap: 30px; }

/* The Bin */
.bin-wrapper { position: relative; width: 160px; height: 280px; display: flex; flex-direction: column; align-items: center; }

/* Animated Lid Container */
.lid-container { display: flex; flex-direction: column; align-items: center; width: 100%; transition: transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1); transform-origin: left bottom; z-index: 10; margin-bottom: -5px; }
.lid-container.open { transform: translateY(-40px) rotate(-40deg); }

/* Black Lid */
.lid { width: 170px; height: 25px; background: #111; border-radius: 12px; border: 2px solid #333; box-shadow: 0 5px 15px rgba(0,0,0,0.5); }
.lid-handle { width: 60px; height: 12px; background: #222; border-radius: 6px 6px 0 0; border: 2px solid #333; border-bottom: none; margin-bottom: -2px; }

/* Wooden Body */
.bin-body { width: 150px; flex: 1; border-radius: 0 0 15px 15px; border: 4px solid #3a2318; border-top: none; position: relative; overflow: hidden; box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
  /* Wood Texture */
  background: 
    linear-gradient(90deg, rgba(0,0,0,0.4) 0%, transparent 20%, transparent 80%, rgba(0,0,0,0.4) 100%),
    repeating-linear-gradient( 90deg, #5c3a21 0px, #5c3a21 10px, #4a2f1a 10px, #4a2f1a 20px );
}

/* Rubber Duck Picture */
.duck-pic { position: absolute; top: 20px; left: 50%; transform: translateX(-50%); z-index: 5; font-size: 40px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.4)); opacity: 0.9; }

/* Liquid / Fill Animation */
.fill-level { position: absolute; bottom: 0; left: 0; width: 100%; height: 0%; background: linear-gradient(180deg, rgba(250, 204, 21, 0.85) 0%, rgba(202, 138, 4, 0.95) 100%); transition: height 1.5s cubic-bezier(0.25, 1, 0.5, 1); box-shadow: 0 -5px 15px var(--accent-glow); }
/* Waves */
.fill-level::before, .fill-level::after { content: ''; position: absolute; width: 300px; height: 300px; top: -150px; left: 50%; transform: translateX(-50%); border-radius: 40%; background: rgba(0,0,0,0.15); animation: spin 6s linear infinite; }
.fill-level::after { top: -140px; border-radius: 45%; background: rgba(255,255,255,0.1); animation: spin 8s linear infinite reverse; }

@keyframes spin { 0% { transform: translateX(-50%) rotate(0deg); } 100% { transform: translateX(-50%) rotate(360deg); } }

/* Data Display */
.stats { text-align: center; width: 100%; }
.pct-text { font-size: 4rem; font-weight: 900; color: var(--accent); line-height: 1; text-shadow: 0 0 30px var(--accent-glow); margin-bottom: 10px; transition: color 0.5s; }
.pct-text span { font-size: 2rem; font-weight: 500; color: var(--text-muted); }

/* Progress Bar */
.prog-container { width: 100%; height: 8px; background: rgba(255,255,255,0.05); border-radius: 4px; overflow: hidden; margin-top: 15px; }
.prog-bar { height: 100%; width: 0%; background: var(--accent); border-radius: 4px; transition: width 1s ease-in-out; box-shadow: 0 0 10px var(--accent); }

/* Status info */
.last-upd { margin-top: 20px; font-size: 0.8rem; color: #666; text-align: center; font-weight: 300; display: flex; align-items: center; justify-content: center; gap: 8px; }
.led { width: 8px; height: 8px; border-radius: 50%; background: #22c55e; box-shadow: 0 0 8px #22c55e; animation: pulse 2s infinite; }
.led.error { background: #ef4444; box-shadow: 0 0 8px #ef4444; }

@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

/* Responsive tweaks */
@media (max-width: 400px) {
  .bin-wrapper { width: 130px; height: 230px; }
  .lid { width: 140px; }
  .bin-body { width: 120px; }
  .duck-pic { font-size: 30px; }
  .pct-text { font-size: 3.5rem; }
}
</style>
</head>
<body>
<div class="bg-gradient"></div>

<div class="app-container">
  <div class="header">
    <h1>Smart Bin</h1>
    <p>Live Volume Monitor</p>
  </div>

  <div class="card">
    <div class="bin-wrapper">
      <div class="lid-container" id="lid-anim">
        <div class="lid-handle"></div>
        <div class="lid"></div>
      </div>
      <div class="bin-body">
        <div class="duck-pic">🦆</div>
        <div class="fill-level" id="liquid"></div>
      </div>
    </div>

    <div class="stats">
      <div class="pct-text" id="pct-val">0<span>%</span></div>
      <div style="color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 2px;">Volume Filled</div>
      <div class="prog-container">
        <div class="prog-bar" id="prog-bar"></div>
      </div>
    </div>
  </div>

  <div class="last-upd">
    <div class="led" id="led-indicator"></div>
    <span id="time-val">Waiting for data...</span>
  </div>
</div>

<script>
async function fetchData() {
  try {
    const res = await fetch('/data');
    if (!res.ok) throw new Error('HTTP error');
    const data = await res.json();
    
    const pct = parseFloat(data.volume).toFixed(1);
    
    // Animate UI
    document.getElementById('liquid').style.height = pct + '%';
    document.getElementById('prog-bar').style.width = pct + '%';
    document.getElementById('pct-val').innerHTML = pct + '<span>%</span>';
    
    // Animate Lid
    if (data.lid_status === 'open') {
        document.getElementById('lid-anim').classList.add('open');
    } else {
        document.getElementById('lid-anim').classList.remove('open');
    }
    
    // Change color based on fullness
    let color = '#facc15'; // default yellow
    if (pct > 80) color = '#ef4444'; // red if > 80%
    else if (pct < 20) color = '#22c55e'; // green if empty
    
    document.getElementById('liquid').style.background = `linear-gradient(180deg, ${color} 0%, rgba(0,0,0,0.5) 150%)`;
    document.getElementById('prog-bar').style.background = color;
    document.getElementById('prog-bar').style.boxShadow = `0 0 10px ${color}`;
    document.getElementById('pct-val').style.color = color;
    document.getElementById('pct-val').style.textShadow = `0 0 30px ${color}66`;

    if (data.last_updated) {
        document.getElementById('time-val').textContent = 'Last update: ' + data.last_updated;
    }
    
    // Green LED
    const led = document.getElementById('led-indicator');
    led.className = 'led'; 
  } catch (err) {
    console.error(err);
    // Red LED on error
    document.getElementById('led-indicator').className = 'led error';
    document.getElementById('time-val').textContent = 'Connection lost. Retrying...';
  }
}

// Fetch every 1 second for snappier animations
fetchData();
setInterval(fetchData, 1000);
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return Response(HTML, content_type="text/html; charset=utf-8")

@app.route("/update", methods=["POST"])
def update():
    global sensor_data
    try:
        body = request.get_json(force=True, silent=True)
        if not body:
            return jsonify({"status": "error", "message": "Invalid JSON"}), 400

        if "volume" in body:
            sensor_data["volume"] = max(0.0, min(100.0, float(body["volume"])))
            sensor_data["last_updated"] = datetime.now().strftime("%I:%M:%S %p")
            print(f"[DATA] Received volume: {sensor_data['volume']}%")
            
        if "lid_status" in body:
            sensor_data["lid_status"] = body["lid_status"]
            print(f"[DATA] Lid is now: {sensor_data['lid_status']}")
            
        return jsonify({"status": "ok", "data": sensor_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/data")
def get_data():
    return jsonify(sensor_data)

if __name__ == "__main__":
    print("\n" + "="*40)
    print(" 🦆 SmartBin Server Running")
    print("="*40)
    print(" Dashboard: http://localhost:5000")
    print("="*40 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=True)