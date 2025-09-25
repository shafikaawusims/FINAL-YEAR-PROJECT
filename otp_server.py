# C:\otp\otp_server.py
import sqlite3, time, csv, os
from flask import Flask, request, jsonify
import pyotp

DB = "C:\\otp\\users.db"
LOG_FILE = "C:\\otp\\logs\\requests.csv"

# set to a positive integer to simulate slower processing
DELAY_MS = 0

app = Flask(__name__)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ts", "client", "endpoint", "user", "code", "result", "latency_ms"])

def db_get_token(username, ttype):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT secret, counter, digits, step, window FROM tokens WHERE username=? AND type=?",
                (username, ttype))
    row = cur.fetchone()
    conn.close()
    return row

def db_set_counter(username, new_counter):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("UPDATE tokens SET counter=? WHERE username=? AND type='hotp'",
                (new_counter, username))
    conn.commit()
    conn.close()

def log_request(ep, user, code, result, started):
    latency_ms = int((time.time() - started) * 1000)
    with open(LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow([int(time.time()), request.remote_addr, ep, user, code, result, latency_ms])

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": True, "value": True})

@app.route("/provision/<username>/<ttype>", methods=["GET"])
def provision(username, ttype):
    row = db_get_token(username, ttype)
    if not row:
        return jsonify({"status": True, "value": False, "error": "no such token"}), 404
    secret, counter, digits, step, window = row
    if ttype == "totp":
        uri = pyotp.TOTP(secret, digits=digits, interval=step).provisioning_uri(
            name=username, issuer_name="LabOTP")
    else:
        uri = pyotp.HOTP(secret, digits=digits).provisioning_uri(
            name=username, issuer_name="LabOTP", initial_count=counter)
    return jsonify({"status": True, "value": True, "username": username, "type": ttype,
                    "secret": secret, "digits": digits, "step": step, "window": window,
                    "otpauth": uri})

@app.route("/verify-totp", methods=["POST"])
def verify_totp():
    started = time.time()
    user = (request.form.get("user") or request.json.get("user") or "").strip()
    code = (request.form.get("code") or request.json.get("code") or "").strip()
    row = db_get_token(user, "totp")
    ok = False
    if row:
        secret, counter, digits, step, window = row
        totp = pyotp.TOTP(secret, digits=digits, interval=step)
        ok = totp.verify(code, valid_window=window)
    if DELAY_MS > 0:
        time.sleep(DELAY_MS / 1000.0)
    log_request("verify-totp", user, code, ok, started)
    return jsonify({"status": True, "value": ok, "type": "totp", "server_time": int(time.time())})

@app.route("/verify-hotp", methods=["POST"])
def verify_hotp():
    started = time.time()
    user = (request.form.get("user") or request.json.get("user") or "").strip()
    code = (request.form.get("code") or request.json.get("code") or "").strip()
    row = db_get_token(user, "hotp")
    ok = False
    counter_used = None
    if row:
        secret, counter, digits, step, window = row
        counter_used = counter
        hotp = pyotp.HOTP(secret, digits=digits)
        ok = hotp.verify(code, counter)
        if ok:
            db_set_counter(user, counter + 1)
    if DELAY_MS > 0:
        time.sleep(DELAY_MS / 1000.0)
    log_request("verify-hotp", user, code, ok, started)
    return jsonify({"status": True, "value": ok, "type": "hotp", "counter_used": counter_used})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
