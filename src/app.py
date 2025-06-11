import os
from flask import Flask, request, jsonify
from EventHandler import EventHandler
import logging
import threading
from dotenv import load_dotenv

load_dotenv()

if os.path.exists("app.log"):
    os.remove("app.log")

# Basic config
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = Flask(__name__)

events_of_interest = set({"app_mention"})

# YOUR APP credentials
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
TEMP_TOKEN = os.getenv("TEMP_TOKEN")

@app.route("/")
def hello():
    return "Hello from Railway!"

@app.route('/slack/events', methods=['POST', 'GET'])
def slack_events():
    data = request.get_json()
    
    # Slack URL verification
    if data.get("type") == "url_verification":
        return jsonify({'challenge': data['challenge']})

    # Handle message events
    # Main event callback handling
    if data.get("type") == "event_callback":
        event = data.get("event", {})
        user = event.get("user")
        text = event.get("text")
        event_type = event.get("type")
        channel_id = event.get("channel")
        files = event.get("files")

        if event_type in events_of_interest:
            event_handler = EventHandler(app.logger, event_type, channel_id, user, text, files)
            app.logger.info(f"{event_type} message from {user}: {text}, channel: {channel_id}")

            # Launch background thread
            threading.Thread(target=event_handler.handle_event).start()

    return '', 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if not set
    app.run(host="0.0.0.0", port=port)