import sqlite3
import os

DB_NAME = "moodle_analytics.db"
SQL_FILE = "init.sql"

if not os.path.exists(SQL_FILE):
    print(f"Nu gesesc fisier: {SQL_FILE}")
    exit()

if os.path.exists(DB_NAME):
    os.remove(DB_NAME)
    print(f"Baza de date veche '{DB_NAME}' a fost stearsa")

try:
    conn = sqlite3.connect(DB_NAME)
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        sql_script = f.read()
        conn.executescript(sql_script)
    print(f"Baza de date: {DB_NAME} a fost creata")
except sqlite3.Error as e:
    print(f"Eroare: {e}")
finally:
    if conn:
        conn.close()