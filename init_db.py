# C:\otp\init_db.py
import os, sqlite3, pyotp

DB = "C:\\otp\\users.db"
os.makedirs("C:\\otp\\logs", exist_ok=True)

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
  username TEXT PRIMARY KEY,
  display_name TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS tokens(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT,
  type TEXT CHECK(type IN ('totp','hotp')),
  secret TEXT,
  counter INTEGER DEFAULT 0,
  digits INTEGER,
  step INTEGER,
  window INTEGER,
  UNIQUE(username, type)
)
""")

def seed_user(u, d):
    cur.execute("INSERT OR IGNORE INTO users(username, display_name) VALUES(?,?)",
                (u, u.capitalize()))
    # new secrets each seed
    tsec = pyotp.random_base32()
    hsec = pyotp.random_base32()
    cur.execute("""INSERT OR REPLACE INTO tokens(username, type, secret, counter, digits, step, window)
                   VALUES(?,?,?,?,?,?,?)""",
                (u, "totp", tsec, 0, d, 30, 1))
    cur.execute("""INSERT OR REPLACE INTO tokens(username, type, secret, counter, digits, step, window)
                   VALUES(?,?,?,?,?,?,?)""",
                (u, "hotp", hsec, 0, d, 30, 1))
    # show URIs and write QR codes
    totp_uri = pyotp.TOTP(tsec, digits=d, interval=30).provisioning_uri(name=u, issuer_name="LabOTP")
    hotp_uri = pyotp.HOTP(hsec, digits=d).provisioning_uri(name=u, issuer_name="LabOTP", initial_count=0)
    print(f"{u} TOTP secret:", tsec)
    print(f"{u} TOTP otpauth:", totp_uri)
    print(f"{u} HOTP secret:", hsec)
    print(f"{u} HOTP otpauth:", hotp_uri)
    try:
        import qrcode
        qrcode.make(totp_uri).save(f"C:\\otp\\{u}_totp_qr.png")
        qrcode.make(hotp_uri).save(f"C:\\otp\\{u}_hotp_qr.png")
        print(f"Saved {u}_totp_qr.png and {u}_hotp_qr.png")
    except Exception as e:
        print("QR creation skipped:", e)

# two users so you can switch without reseeding
seed_user("alice4", 4)   # short demo user
seed_user("alice6", 6)   # realistic user

conn.commit()
conn.close()
print("Database initialized at C:\\otp\\users.db")
