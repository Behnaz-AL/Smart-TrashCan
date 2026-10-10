import serial
import time
import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
# IMPORTANT: Change this to your Arduino's COM port! (e.g., 'COM3', 'COM4', 'COM5')
PORT = 'COM3' 
BAUD = 9600
FLASK_URL = 'http://127.0.0.1:5000/update'

# Bin calibration (cm)
BIN_EMPTY_CM = 16.0  # Distance when completely empty
BIN_FULL_CM = 2.0    # Distance when completely full

# --- TELEGRAM BOT CONFIG ---
# 1. Message @BotFather on Telegram to create a bot and get a Token
# 2. Message @userinfobot to get your Chat ID
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")
telegram_alert_sent = False

def send_telegram_alert(volume_pct):
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE" or TELEGRAM_CHAT_ID == "YOUR_CHAT_ID_HERE":
        return # Skip if not configured
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    msg = f"🚨 *ALERT:* The Smart Trash Bin is almost full ({volume_pct:.1f}%)! Please empty it."
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=2)
        print(" ╰─> [TELEGRAM] Sent full bin alert!")
    except Exception as e:
        print(f" ╰─> [TELEGRAM ERROR] Could not send message: {e}")

print("=========================================")
print(" SmartBin Local Serial Bridge")
print("=========================================")

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"[SUCCESS] Connected to Arduino on {PORT}")
    time.sleep(2) # Wait for Arduino to reset
except Exception as e:
    print(f"[ERROR] Could not connect to {PORT}: {e}")
    print("\n>>> PLEASE CHANGE 'PORT' IN THIS SCRIPT TO YOUR ACTUAL ARDUINO COM PORT <<<")
    exit(1)

current_lid_state = "closed"

while True:
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            
            # Print everything the Arduino says
            if line:
                print(f"[Arduino] {line}")
            
            # Check for lid status (supports both new LID_STATUS and old target outputs)
            if "LID_STATUS: OPEN" in line or "target: 400" in line:
                if current_lid_state != "open":
                    current_lid_state = "open"
                    print(" ╰─> Lid is opening! Sending to Dashboard...")
                    try:
                        requests.post(FLASK_URL, json={"lid_status": "open"}, timeout=1)
                    except requests.exceptions.RequestException:
                        pass
            elif "LID_STATUS: CLOSED" in line or "target: 200" in line:
                if current_lid_state != "closed":
                    current_lid_state = "closed"
                    print(" ╰─> Lid is closing! Sending to Dashboard...")
                    try:
                        requests.post(FLASK_URL, json={"lid_status": "closed"}, timeout=1)
                    except requests.exceptions.RequestException:
                        pass
                    
            # Extract the depth if we see "Trash depth: XX cm"
            match = re.search(r'Trash depth:\s*(\d+)', line)
            if match:
                distance = float(match.group(1))
                
                # Calculate percentage
                pct = 0.0
                if distance < 999:
                    pct = ((BIN_EMPTY_CM - distance) / (BIN_EMPTY_CM - BIN_FULL_CM)) * 100.0
                    pct = max(0.0, min(100.0, pct))
                    
                print(f" ╰─> Calculated Volume: {pct:.1f}% -> Sending to Dashboard...")
                
                # Telegram Alert Logic
                if pct >= 90.0 and not telegram_alert_sent:
                    send_telegram_alert(pct)
                    telegram_alert_sent = True
                elif pct < 80.0:
                    telegram_alert_sent = False # Reset when emptied
                
                # Send to Flask app local dashboard
                try:
                    requests.post(FLASK_URL, json={"volume": pct}, timeout=1)
                except requests.exceptions.RequestException:
                    print("     [!] Failed to update dashboard. Is app.py running?")
                    
    except KeyboardInterrupt:
        print("\n[INFO] Exiting...")
        break
    except Exception as e:
        print(f"[ERROR] Connection lost: {e}")
        break

ser.close()
