import sqlite3, os

DB = os.path.join("data","wipe_logs.db")

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device TEXT, method TEXT, passes INTEGER,
        start_time REAL, end_time REAL,
        sha_before TEXT, sha_after TEXT,
        status TEXT, report_path TEXT
    )""")
    conn.commit()
    conn.close()

def insert_log(device, method, passes, start_time, end_time, sha_before, sha_after, status, report_path):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO logs (device,method,passes,start_time,end_time,sha_before,sha_after,status,report_path) VALUES (?,?,?,?,?,?,?,?,?)",
              (device,method,passes,start_time,end_time,sha_before,sha_after,status,report_path))
    conn.commit()
    conn.close()
