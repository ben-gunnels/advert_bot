import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")
DROPBOX_USER_ID = os.getenv("DROPBOX_USER_ID")

def list_team_members():
    url = "https://api.dropboxapi.com/2/team/members/list"
    headers = {
        "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "limit": 100
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        members = response.json()
        return members
    else:
        print("Failed to list team members:", response.text)
        return None

# Run the function
if __name__ == "__main__":
    members = list_team_members()
    if members:
        for member in members.get("members", []):
            print(f"User: {member['profile']['name']['display_name']} - User ID: {member['profile']['team_member_id']}")


def list_shared_folders_for_user(user_id):
    url = "https://api.dropboxapi.com/2/sharing/list_folders"
    headers = {
        "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
        "Dropbox-API-Select-User": user_id,
        "Content-Type": "application/json"
    }
    data = {
        "limit": 100
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        folders = response.json()
        return folders
    else:
        print("Failed to list shared folders:", response.text)
        return None

# Example usage
user_id = DROPBOX_USER_ID
shared_folders = list_shared_folders_for_user(user_id)
if shared_folders:
    print("Shared Folders for Selected User:")
    for folder in shared_folders.get("entries", []):
        print(f"Shared Folder: {folder.get('name')} - Shared Folder ID: {folder.get('shared_folder_id')}")
