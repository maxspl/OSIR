import os
import string

def find_single_letter_directory(path):
    """
    Find directories that are named with a single uppercase letter in the given path.
    """
    for directory in os.listdir(path):
        if os.path.isdir(os.path.join(path, directory)) and len(directory) == 1 and directory in string.ascii_uppercase:
            return os.path.join(path, directory)
    return None


def find_usernames(folder_path):
    usernames = []
    for username in os.listdir(folder_path + "/Users"):
        if username == "Default":
            pass
        else:
            usernames.append(username)
    return usernames


def determine_browser(path):
    files = os.listdir(path)
    for file in files:
        if file.lower() == "chrome icon.ico":
            return "chrome"
        elif file.lower() == "edge icon.ico":
            return "edge"
        elif "firefox" in path.lower():
            return "firefox"
        elif file.lower() == "readme":
            if "Opera" in file.readlines():
                return "opera"
        else:
            return "unknown"


def locate_browser_directories(path):
    
    # Check for a single letter directory first, and use that as the "starting point"
    letter_dir = find_single_letter_directory(path)
        
    if letter_dir:
        path = letter_dir  # Update path to the single letter directory


    user_dir = {}
    for username in find_usernames(path):
        appdata = f"{path}/Users/{username}/AppData"
        return_val = {}
        if os.path.exists(f"{appdata}/Roaming/Mozilla/Firefox/Profiles/"):
            user_profiles = [a for a in os.listdir(f"{appdata}/Roaming/Mozilla/Firefox/Profiles/")]
            directories = []
            for profile in user_profiles:
                directories.append(f"{appdata}/Roaming/Mozilla/Firefox/Profiles/{profile}")

            return_val["Firefox"] = tuple(directories)
        if os.path.exists(f"{appdata}/Local/Google/Chrome/User Data/Default"):
            return_val["Chrome"] = f"{appdata}/Local/Google/Chrome/User Data/Default"
        if os.path.exists(f"{appdata}/Local/Microsoft/Edge/User Data/Default"):
            return_val["Edge"] = f"{appdata}/Local/Microsoft/Edge/User Data/Default"

        if os.path.exists(f"{appdata}/Roaming/Opera Software/Opera Stable/Default"):
            return_val["Opera"] = f"{appdata}/Roaming/Opera Software/Opera Stable/Default"

        user_dir[username] = return_val
    return user_dir
