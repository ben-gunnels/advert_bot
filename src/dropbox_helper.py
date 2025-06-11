import os
import pathlib
import pathlib
import requests
import json
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
APP_KEY = os.getenv("DROPBOX_APP_KEY")
APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
USER_ID = os.getenv("DROPBOX_USER_ID")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
MODELS_FOLDER_ID = os.getenv("MODELS_FOLDER_ID")

# Endpoint to get the access token
DROPBOX_TOKEN_URL = "https://api.dropboxapi.com/oauth2/token"

def get_access_token(app_key, app_secret, refresh_token):
    """
    Uses the refresh token to get a new short-lived access token.
    """
    basic_auth = base64.b64encode(f"{app_key}:{app_secret}".encode()).decode()

    headers = {
        "Authorization": f"Basic {basic_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post(DROPBOX_TOKEN_URL, headers=headers, data=data)
    response.raise_for_status()

    return response.json()["access_token"]

def list_subfolders(folder_path: str, folder_id: str):
    """
    Lists the subfolders inside a Dropbox folder given its path and namespace id.
    """
    # Exchange refresh token for short-lived access token
    try:
        access_token = get_access_token(APP_KEY, APP_SECRET, DROPBOX_REFRESH_TOKEN)
    except Exception as e:
        return {"error": "Failed to get access token", "details": str(e)}
    
    url = "https://api.dropboxapi.com/2/files/list_folder"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Dropbox-API-Select-User": USER_ID,
        "Dropbox-API-Path-Root": json.dumps({
            ".tag": "namespace_id",
            "namespace_id": folder_id
        }),
        "Content-Type": "application/json"
    }

    data = {
        "path": folder_path,   # e.g. "" for root of shared folder
        "recursive": False,    # Set to True if you want full tree
        "include_media_info": False,
        "include_deleted": False
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()

        entries = response.json().get('entries', [])
        subfolders = [entry for entry in entries if entry['.tag'] == 'folder']
        return subfolders

    except requests.RequestException as e:
        return {"error": str(e)}
    
def count_files_in_subfolder(folder_id: str, subfolder_path: str):
    """
    Counts the number of files in a subfolder inside a Dropbox shared folder.
    
    :param folder_id: Dropbox namespace_id for shared folder
    :param subfolder_path: Subfolder path inside shared folder (e.g. "/folderA/subfolderB")
    :param access_token: OAuth token
    :param user_id: Dropbox user ID
    """
    # Exchange refresh token for short-lived access token
    try:
        access_token = get_access_token(APP_KEY, APP_SECRET, DROPBOX_REFRESH_TOKEN)
    except Exception as e:
        return {"error": "Failed to get access token", "details": str(e)}
    
    url = "https://api.dropboxapi.com/2/files/list_folder"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Dropbox-API-Select-User": USER_ID,
        "Dropbox-API-Path-Root": json.dumps({
            ".tag": "namespace_id",
            "namespace_id": folder_id
        }),
        "Content-Type": "application/json"
    }

    data = {
        "path": subfolder_path,
        "recursive": False,    # Only immediate files in that folder
        "include_media_info": False,
        "include_deleted": False
    }

    file_count = 0
    has_more = True

    try:
        while has_more:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()

            entries = result.get('entries', [])
            file_count += sum(1 for entry in entries if entry['.tag'] == 'file')

            # Handle pagination
            if result.get('has_more'):
                url_continue = "https://api.dropboxapi.com/2/files/list_folder/continue"
                data = {"cursor": result['cursor']}
                url = url_continue
            else:
                has_more = False

        return {"file_count": file_count}

    except requests.RequestException as e:
        return {"error": str(e)}

def download_file_from_shared_folder(folder_id: str, file_path: str, download_to: str):
    """
    Downloads a file (e.g., image) from a shared Dropbox folder using namespace ID.
    
    :param folder_id: Dropbox namespace_id for the shared folder
    :param file_path: Path to file inside shared folder (e.g. "/image.jpg")
    :param access_token: OAuth access token
    :param user_id: Dropbox user ID
    :param download_to: Local path to save downloaded file
    """
    try:
        access_token = get_access_token(APP_KEY, APP_SECRET, DROPBOX_REFRESH_TOKEN)
    except Exception as e:
        return {"error": "Failed to get access token", "details": str(e)}
    
    url = "https://content.dropboxapi.com/2/files/download"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Dropbox-API-Select-User": USER_ID,
        "Dropbox-API-Path-Root": json.dumps({
            ".tag": "namespace_id",
            "namespace_id": folder_id
        }),
        "Dropbox-API-Arg": json.dumps({
            "path": file_path
        })
    }

    try:
        response = requests.post(url, headers=headers, stream=True)
        response.raise_for_status()

        with open(download_to, 'wb') as f:
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
        
        return {"message": f"File downloaded successfully to {download_to}"}
    
    except requests.RequestException as e:
        return {"error": "Failed to download file", "details": str(e)}

def upload_to_shared_folder(file_path: str, folder_id):
    """
        Uploads a given file path to a shared dropbox folder. 
        The function must be supplied a known file ID and user id to perform this request. 
    """
    # Convert file path to a Path object
    file = pathlib.Path(file_path)
    
    if not file.exists():
        return {"error": "File does not exist"}
    
    # Exchange refresh token for short-lived access token
    try:
        access_token = get_access_token(APP_KEY, APP_SECRET, DROPBOX_REFRESH_TOKEN)
    except Exception as e:
        return {"error": "Failed to get access token", "details": str(e)}
    
    # Read the file content
    file_content = file.read_bytes()
    file_name = file.name

    # Specify the Dropbox path using the shared folder ID
    dropbox_path = f"/{file_name}"  # The file will appear in the root of the shared folder

    url = "https://content.dropboxapi.com/2/files/upload"

    # Set the request headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Dropbox-API-Select-User": USER_ID,
        "Dropbox-API-Path-Root": json.dumps({
            ".tag": "namespace_id",
            "namespace_id": folder_id
        }),
        "Content-Type": "application/octet-stream",
        "Dropbox-API-Arg": json.dumps({
            "path": dropbox_path,
            "mode": "add",
            "autorename": True,
            "mute": False
        })
    }

    # print("Uploading to Dropbox Shared Folder...")
    # print(f"User ID: {USER_ID}")
    # print(f"Shared Folder ID: {folder_id}")
    # print(f"Dropbox Path: {dropbox_path}")

    try:
        response = requests.post(url, headers=headers, data=file_content)
        print(f"Response Status: {response.status_code}")
        # print(f"Response Text: {response.text}")
        response.raise_for_status()  # This will raise an error for non-200 responses
        return {"message": "File uploaded successfully", "dropbox_path": dropbox_path}

    except requests.RequestException as e:
        print(f"Error Details: {str(e)}")
        return {"error": "Failed to upload file to Dropbox", "details": str(e)}

def main():
    file_count = count_files_in_subfolder(MODELS_FOLDER_ID, "/female/red")
    print(file_count)

if __name__ == "__main__":
    main()