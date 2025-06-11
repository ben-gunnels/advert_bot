import os
from dotenv import load_dotenv

__all__ = ["CHANNEL_MAP", "MODEL_ATTRIBUTES"]

load_dotenv()
DROPBOX_ID = os.getenv("DESIGN_ADS_DROPBOX")
VALID_CHANNEL_1 = os.getenv("VALID_CHANNEL_1")

VALID_CHANNEL_2 = os.getenv("VALID_CHANNEL_2")

VALID_CHANNEL_3 = os.getenv("VALID_CHANNEL_3")

VALID_CHANNEL_4 = os.getenv("VALID_CHANNEL_4")

VALID_CHANNEL_5 = os.getenv("VALID_CHANNEL_5")

CHANNEL_MAP = {
    VALID_CHANNEL_1: DROPBOX_ID,
    VALID_CHANNEL_2: DROPBOX_ID,
    VALID_CHANNEL_3: DROPBOX_ID,
    VALID_CHANNEL_4: DROPBOX_ID,
    VALID_CHANNEL_5: DROPBOX_ID
}

MODEL_ATTRIBUTES = {
    "sex": set(["male", "female"]),
    "shirt-color": set(["white", "black", "red", "blue"])
}

MODEL_FOLDER_DIRECTORY = {
    "male": {
        "white": "",
        "black": "",
        "red": "",
        "blue": ""
    },
    "female": {
        "white": "",
        "black": "",
        "red": "",
        "blue": ""
    }
}