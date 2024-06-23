from flask import Flask, request
import json
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_file_url(file_id):
    response = requests.get(f"{BASE_URL}/getFile?file_id={file_id}")
    result = response.json()
    if result["ok"]:
        file_path = result["result"]["file_path"]
        return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    return None

def save_file_locally(file_url, file_name):
    response = requests.get(file_url)
    with open(f"files/{file_name}", "wb") as file:
        file.write(response.content)
    return f"https://yourdomain.com/files/{file_name}"

@app.route('/', methods=['POST'])
def webhook():
    update = request.get_json()
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        message_id = message["message_id"]

        if "document" in message:
            file_id = message["document"]["file_id"]
            file_url = get_file_url(file_id)
            if file_url:
                file_name = message["document"]["file_name"]
                download_url = save_file_locally(file_url, file_name)
                send_message(chat_id, message_id, download_url)

    return "OK"

def send_message(chat_id, reply_to_message_id, text):
    url = f"{BASE_URL}/sendMessage"
    data = {
        "chat_id": chat_id,
        "reply_to_message_id": reply_to_message_id,
        "text": text
    }
    requests.post(url, data=data)

if __name__ == "__main__":
    app.run(debug=True)
