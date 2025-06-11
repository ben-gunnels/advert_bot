import os
import requests
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

__all__ = [
    "get_channel_id",
    "send_message",
    "download_slack_file",
    "send_file"
]

SLACK_TOKEN = os.getenv("SLACK_TOKEN")

client = WebClient(token=SLACK_TOKEN, timeout=180)

def get_all_channel_ids():
    channels = {}
    try:
        for result in client.conversations_list(types="public_channel,private_channel"):
            for channel in result["channels"]:
                channels[channel["name"]] = channel["id"]
        return channels
    except SlackApiError as e:
        print(f"Error: {e}")

def get_channel_id(channel_name):
    conversation_id = None
    try:
        # Call the conversations.list method using the WebClient
        for result in client.conversations_list():
            if conversation_id is not None:
                break
            for channel in result["channels"]:
                if channel["name"] == channel_name:
                    conversation_id = channel["id"]
                    print(f"Found conversation ID: {conversation_id}")
                    break

    except SlackApiError as e:
        print(f"Error: {e}")

def send_message(channel_id, message):
    try:
        # Call the conversations.list method using the WebClient
        result = client.chat_postMessage(
            channel=channel_id,
            text=message
            # You could also use a blocks[] array to send richer content
        )

    except SlackApiError as e:
        print(f"Error: {e}")

def download_slack_file(file_url, local_filename, token=SLACK_TOKEN):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(file_url, headers=headers)
    if response.status_code == 200:
        with open(local_filename, "wb") as f:
            f.write(response.content)
        print(f"Saved to {local_filename}")
    else:
        print(f"Failed to download: {response.status_code}, {response.text}")

def send_file(channel_id, filename, message="Here’s an AI-generated Image! 🎨"):
    with open(filename, "rb") as f:
        try:
            response = client.files_upload_v2(
                channel=channel_id,
                initial_comment=message,
                file_uploads=[
                    {
                        "file": f,
                        "filename": filename,
                        "title": "Generated Image"
                    }
                ]
            )
            print(f"Upload successful! File ID: {response['file']['id']}")
        except Exception as e:
            print(f"Error uploading file: {e}")