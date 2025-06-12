import re
import shutil
import time
import datetime

def remove_directory_recursively(path):
    """
    Removes a directory recursively.

    Args:
        path: The path to the directory to remove.
    """
    try:
        shutil.rmtree(path)
        print(f"Directory '{path}' and its contents have been removed successfully.")
    except FileNotFoundError:
        print(f"Error: Directory '{path}' not found.")
    except OSError as e:
       print(f"Error: Could not remove directory '{path}'. Reason: {e}")

def find_flags(text):
    pattern = r'--(\w+)'  # Look for -- followed by letters, digits, underscores
    flags = re.findall(pattern, text)
    return set(flags)

def clean_text(text):
    # Remove things in angle brackets
    text = re.sub(r'<[^>]+>', '', text)

    # Remove flags starting with --
    text = re.sub(r'\s--\S+', '', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text

def get_series(text):
    """
        Gets the series literals and returns them in a list.
    """
    series = list(re.findall(r"\{.*?\}", text))
    return series

def get_attributes(text):
    """
        Returns a list of attributes that are used to select a model for the advertisement.
            e.g. ['female', 'white'] returns a female model wearing a white shirt. 
    """
    raw = list(re.findall(r"\{(.*?)\}", text))

    attributes = [c.strip().lower() for c in raw[0].split(",")]

    return attributes[:2] # Return only the first two items

# Convert a date string to Unix timestamp
def to_unix_timestamp(date_str):
    return int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple()))

def get_today_unix_range():
    # Get today's date at midnight
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_ts = int(time.mktime(today.timetuple()))
    
    # Get end of today (11:59:59 PM)
    end_ts = int(time.mktime((today + datetime.timedelta(days=1, seconds=-1)).timetuple()))

    return start_ts, end_ts

