import os
from dotenv import load_dotenv

__all__ = ["CHANNEL_MAP"]

VALID_CHANNEL_1 = os.getenv("VALID_CHANNEL_1")
DROPBOX_1 = str(os.getenv("DROPBOX_1"))

VALID_CHANNEL_2 = os.getenv("VALID_CHANNEL_2")
DROPBOX_2 = str(os.getenv("DROPBOX_2"))

VALID_CHANNEL_3 = os.getenv("VALID_CHANNEL_3")
DROPBOX_3 = str(os.getenv("DROPBOX_3"))

VALID_CHANNEL_4 = os.getenv("VALID_CHANNEL_4")
DROPBOX_4 = str(os.getenv("DROPBOX_4"))

VALID_CHANNEL_5 = os.getenv("VALID_CHANNEL_5")
DROPBOX_5 = str(os.getenv("DROPBOX_5"))

VALID_CHANNEL_6 = os.getenv("VALID_CHANNEL_6")
DROPBOX_6 = str(os.getenv("DROPBOX_6"))

VALID_CHANNEL_7 = os.getenv("VALID_CHANNEL_7")
DROPBOX_7 = str(os.getenv("DROPBOX_7"))

CHANNEL_MAP = {
    VALID_CHANNEL_1: DROPBOX_1,
    VALID_CHANNEL_2: DROPBOX_2,
    VALID_CHANNEL_3: DROPBOX_3,
    VALID_CHANNEL_4: DROPBOX_4,
    VALID_CHANNEL_5: DROPBOX_5,
    VALID_CHANNEL_6: DROPBOX_6,
    VALID_CHANNEL_7: DROPBOX_7
}