import os
import time
from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
            host=os.environ.get("DB_HOST", "${DB_HOST}"),
            user=os.environ.get("DB_USER", "${DB_USER}"),
            password=os.environ.get("DB_PASSWORD", "${DB_PASSWORD}"),
            database=os.environ.get("DB_NAME", "${DB_NAME}"))

def init_db():
    for _ in range(5):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                name VARCHAR(255) NOT NULL, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            break
        except mysql.connector.Error:
            time.sleep(3)

@app.route("/items", methods=["POST"])
def add_item():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "The 'name' field is required to fill"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items(name) VALUES (%s)", (data["name"],))
    conn.commit()
    item_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({"id": item_id, "name":data["name"]}), 201

@app.route("/items", methods=["GET"])
def view_items():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
