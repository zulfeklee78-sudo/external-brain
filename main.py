from flask import Flask, request, jsonify
import json
import os
import requests

app = Flask(__name__)

# Local memory file
DATA_FILE = "memory.json"

# Load or create memory
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"notes": []}, f)

with open(DATA_FILE, "r") as f:
    memory = json.load(f)

# Notion config
NOTION_TOKEN = "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"
DATABASE_ID = "2ad36058-3fee-80d1-834a-000b76a63eec"
NOTION_URL = f"https://api.notion.com/v1/pages"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def push_to_notion(content):
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [
                    {"text": {"content": content}}
                ]
            }
        }
    }
    response = requests.post(NOTION_URL, headers=HEADERS, json=data)
    return response.status_code == 200 or response.status_code == 201

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "alive", "memory_size": len(memory["notes"])})

@app.route("/add", methods=["POST"])
def add():
    data = request.json.get("data")
    if not data:
        return jsonify({"ok": False, "error": "No data provided"}), 400

    # Save locally
    memory["notes"].append(data)
    with open(DATA_FILE, "w") as f:
        json.dump(memory, f)

    # Push to Notion
    notion_result = push_to_notion(data)
    return jsonify({"ok": True, "stored": data, "notion_pushed": notion_result})

@app.route("/all", methods=["GET"])
def all_notes():
    return jsonify(memory["notes"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
