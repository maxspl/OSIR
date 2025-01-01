from datetime import datetime
import sqlite3
import json
import os
from itertools import groupby
from operator import itemgetter
from lib.output import outputWriter  # type: ignore


def parse_firefox_data(user, directory, profile, output, args):
    print(f"[*] Starting to parse firefox profile {profile}")
    places_dict = {}
    global firefoxWriter
    global out
    out = args
    firefoxWriter = outputWriter(output, user, "firefox", profile)
    parse_cookies(f"{directory}/cookies.sqlite")
    parse_formhistory(f"{directory}/formhistory.sqlite")
    parse_perms(f"{directory}/permissions.sqlite")
    parse_bookmarks(f"{directory}/places.sqlite")
    parse_history(f"{directory}/places.sqlite", places_dict)
    enrich_history(f"{directory}/places.sqlite", places_dict)
    parse_inputhistory(f"{directory}/places.sqlite", places_dict)
    parse_history_metadata(f"{directory}/places.sqlite", places_dict)
    parse_extensions(f"{directory}/extensions.json")
    parse_logins(f"{directory}/logins.json")
    parse_downloads(f"{directory}/places.sqlite", places_dict)
    parse_favicons(f"{directory}/favicons.sqlite")
    parse_notifications(f"{directory}/notificationstore.json")


def connect_database(database_path: str):
    """Establish connection to the SQLite database."""
    try:
        if os.path.exists(database_path):
            connection = sqlite3.connect(f"file:{database_path}?mode=ro&immutable=1", uri=True)
            return connection
        else:
            return None
    except Exception as e:  # Dont raise an error if a file is missing / damaged / etc. Just keep parsing the other files
        print(f"[!] Database connection error: {e}")
        return None


def convert_firefox_time(timestamp: int):

    length = len(str(timestamp))

    if length == 10:  # Seconds

        dt = datetime.fromtimestamp(timestamp)

    elif length == 13:  # Milliseconds

        dt = datetime.fromtimestamp(timestamp / 1000)

    else:  # Microseconds (PRTime)

        dt = datetime.fromtimestamp(timestamp / 1_000_000)

    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def parse_favicons(database: str):
    """Parse favicons from the Firefox SQLite database and save it to a CSV file"""
    connection = connect_database(database)
    if not connection:
        return None
    try:
        cursor = connection.execute("SELECT * FROM moz_pages_w_icons")
        entries = cursor.fetchall()
    except Exception as e:
        print(e)
        return 0
    output = []
    output.append(["page_url"])
    for entry in entries:
        output.append([entry[1]])
    if out.csv:
        firefoxWriter.write_csv("favicon", output)
    if out.json:
        firefoxWriter.write_json("favicon", output)
    if out.html:
        firefoxWriter.write_html("favicon", output)


def parse_extensions(database: str):
    if os.path.exists(database):
        data = json.load(open(f"{database}", "r", encoding="UTF-8"))
        addons: dict = data.get("addons")
        output: list = []
        output.append(["id", "sourceURI", "version", "type", "name", "description", "creator", "installDate", "updateDate", "userPermissions", "optionalPermissions"])

        for addon in addons:
            # I'm using <dict>.get() instead of <dict>[key], because using get() ensures that if the element doesn't exist, I can specify a "replacement" value
            # by doing <dict>.get("nonexistent", "No field named nonexistent found").
            output.append([addon.get("id", "No id specified"),
                           addon.get("sourceURI", "No source URI specified"),
                           addon.get("version", "No version specified"),
                           addon.get("type", "No type specified"),
                           addon.get("defaultLocale").get("name", "No name specified"),
                           addon.get("defaultLocale").get("description", "No description"),
                           addon.get("defaultLocale").get("creator", "No creator specified"),
                           convert_firefox_time(addon.get("installDate", 0)),
                           convert_firefox_time(addon.get("updateDate", 0)),
                           addon.get("userPermissions", "No user permissions specified"),
                           addon.get("optionalPermissions", "No optional permissions specified")])
        if out.csv:
            firefoxWriter.write_csv("extensions", output)
        if out.json:
            firefoxWriter.write_json("extensions", output)
        if out.html:
            firefoxWriter.write_html("extensions", output)


def parse_cookies(database: str):
    """Parse cookies from the Firefox SQLite database and save it to a CSV file"""
    connection = connect_database(database)
    if not connection:
        return None
    try:
        cursor = connection.execute("SELECT * FROM moz_cookies")
        entries = cursor.fetchall()
    except Exception as e:
        print(e)
        return 0
    output = []
    output.append(
        ["name", "value", "host", "expiry", "lastAccessed", "creationTime"]
        )
    for entry in entries:
        output.append(
            [
                entry[2],
                entry[3],
                entry[4],
                convert_firefox_time(entry[6]),
                convert_firefox_time(entry[7]),
                convert_firefox_time(entry[8]),
            ]
        )
    if out.csv:
        firefoxWriter.write_csv("cookies", output)
    if out.json:
        firefoxWriter.write_json("cookies", output)
    if out.html:
        firefoxWriter.write_html("cookies", output)


def parse_formhistory(database: str):
    """Parse form history from the Firefox SQLite database and save it to a CSV file"""

    connection = connect_database(database)
    if not connection:
        return None
    try:
        cursor = connection.execute("SELECT * FROM moz_formhistory")
        entries = cursor.fetchall()
    except Exception as e:
        print(e)
        return 0
    output = []
    output.append(
        ["fieldname", "value", "timesUsed", "firstUsed", "lastUsed"]
    )
    for entry in entries:
        output.append(
            [
                entry[1],
                entry[2],
                entry[3],
                convert_firefox_time(entry[4]),
                convert_firefox_time(entry[5]),
            ]
        )
    if out.csv:
        firefoxWriter.write_csv("formhistory", output)
    if out.json:
        firefoxWriter.write_json("formhistory", output)
    if out.html:
        firefoxWriter.write_html("formhistory", output)


def parse_perms(database: str):
    """Parse permissions from the Firefox SQLite database and save it to a CSV file"""

    connection = connect_database(database)
    if not connection:
        return None
    try:
        cursor = connection.execute("SELECT * FROM moz_perms")
        entries = cursor.fetchall()
    except Exception as e:
        print(e)
        return 0
    output = []
    output.append(["origin", "type", "expireTime", "modificationTime"])
    for entry in entries:
        output.append(
            [
                entry[1],
                entry[2],
                convert_firefox_time(entry[5]),
                convert_firefox_time(entry[6]),
            ]
        )
    if out.csv:
        firefoxWriter.write_csv("permissions", output)
    if out.json:
        firefoxWriter.write_json("permissions", output)
    if out.html:
        firefoxWriter.write_html("permissions", output)


def parse_bookmarks(database: str):
    """Parse bookmarks from the Firefox SQLite database and save it to a CSV file"""

    connection = connect_database(database)
    if not connection:
        return None
    try:
        cursor = connection.execute("SELECT * FROM moz_bookmarks")
        entries = cursor.fetchall()
    except Exception as e:
        print(e)
        return 0
    output = []
    output.append(["title", "dateAdded", "lastModified"])
    for entry in entries:
        output.append(
            [
                entry[5],  # Title
                convert_firefox_time(entry[8]),  # dateAdded
                convert_firefox_time(entry[9]),  # lastModified
            ]
        )
    if out.csv:
        firefoxWriter.write_csv("bookmarks", output)
    if out.json:
        firefoxWriter.write_json("bookmarks", output)
    if out.html:
        firefoxWriter.write_html("bookmarks", output)


def parse_inputhistory(database: str, places_dict: dict):
    """Parse inputhistory from the Firefox SQLite database and save it to a CSV file"""
    connection = connect_database(database)
    if not connection:
        return None
    try:
        cursor = connection.execute("SELECT * FROM moz_inputhistory")
        entries = cursor.fetchall()
    except Exception as e:
        print(e)
        return 0
    output = []
    output.append(["places_id", "url", "input"])
    for entry in entries:
        output.append([entry[0], places_dict[entry[0]][0], entry[1]])
    if out.csv:
        firefoxWriter.write_csv("inputhistory", output)
    if out.json:
        firefoxWriter.write_json("inputhistory", output)
    if out.html:
        firefoxWriter.write_html("inputhistory", output)


def parse_history(database: str, places_dict: dict):
    """Parse history from the Firefox SQLite database and save it to a CSV file"""

    connection = connect_database(database)
    if not connection:
        return None
    try:
        cursor = connection.execute("SELECT * FROM moz_places")
        entries = cursor.fetchall()
    except Exception as e:
        print(e)
        return 0
    output = []
    output.append(
        [
            "id",
            "url",
            "title",
            "host",
            "visit_count",
            "last_visit_date",
            "description",
            "preview_image_url",
        ]
    )
    for entry in entries:
        places_dict[entry[0]] = [entry[1], entry[2], entry[3][::-1][1::], entry[4]]
        if entry[8]:
            output.append(

                [
                    entry[0],
                    entry[1],
                    entry[2],
                    entry[3][::-1][1::],
                    entry[4],
                    convert_firefox_time(entry[8]),
                    entry[12],
                    entry[13],
                ]
            )
        else:
            output.append(

                    [
                        entry[0],
                        entry[1],
                        entry[2],
                        entry[3][::-1][1::],
                        entry[4],
                        "Invalid timestamp",
                        entry[12],
                        entry[13],
                    ]
                )
    if out.csv:
        firefoxWriter.write_csv("history", output)
    if out.json:
        firefoxWriter.write_json("history", output)
    if out.html:
        firefoxWriter.write_html("history", output)


def enrich_history(database: str, places_dict: dict):

    """Parse history metadata from the Firefox SQLite database and save it to a CSV file."""
    connection = connect_database(database)
    if not connection:
        return None
    try:
        cursor = connection.execute("SELECT * FROM moz_historyvisits")
        entries = cursor.fetchall()
    except Exception as e:
        print(e)
        return 0
    output = []
    # Defined in the source code
    # Link: https://searchfox.org/mozilla-central/source/toolkit/components/places/History.sys.mjs Line 762
    visit_types = {"1": "TRANSITION_LINK (User followed a link and got a new toplevel window)",  # If transition reason isn't specified, this is the default
                   "2": "TRANSITION_TYPED (User typed the pages url in the URL bar or selected it from the URL Bar autocomplete result)",
                   "3": "TRANSITION_BOOKMARK (User followed a bookmark to get to the page)",
                   "4": "TRANSITION_EMBED (User followed a link on a page that was embedded in another page (iframe))",
                   "5": "TRANSITION_REDIRECT_PERMANENT (Permanent redirect",
                   "6": "TRANSITION_REDIRECT_TEMPORARY (Temporary redirect)",
                   "7": "TRANSITION_DOWNLOAD (User downloaded the file)",
                   "8": "TRANSITION_FRAMED_LINK (User followed a link and got a visit in a frame)",
                   "9": "TRANSITION_RELOAD (User reloaded the page)"}

    entries.sort(key=itemgetter(2))

    output.append(["from_visit", "place_id", "url", "visit_date", "visit_type"])
    for key, group in groupby(entries, key=itemgetter(2)):
        for item in group:
            output.append([item[1], item[2], places_dict[item[2]][0], convert_firefox_time(item[3]), visit_types[str(item[4])]])
    if out.csv:
        firefoxWriter.write_csv("historyvisits", output)
    if out.json:
        firefoxWriter.write_json("historyvisits", output)
    if out.html:
        firefoxWriter.write_html("historyvisits", output)


def parse_history_metadata(database: str, places_dict: dict):
    """Parse history metadata from the Firefox SQLite database and save it"""
    connection = connect_database(database)
    if not connection:
        return None
    try:
        cursor = connection.execute("SELECT * FROM moz_places_metadata")
        entries = cursor.fetchall()
    except Exception as e:
        print(e)
        return 0
    output = []
    output.append(
        [
            "places_id",
            "url",
            "title",
            "host",
            "visit_count",
            "total_view_time_miliseconds",
            "typing_time_miliseconds",
            "key_presses",
            "scrolling_time_miliseconds",
            "scrolling_distance_mm",  # Why is all this data being logged??
        ]
    )

    # Aggregate times for each unique ID
    times = {}
    for entry in entries:
        if entry[1] in times.keys():
            times[entry[1]][0] += entry[5]
            times[entry[1]][1] += entry[6]
            times[entry[1]][2] += entry[7]
            times[entry[1]][3] += entry[8]
            times[entry[1]][4] += entry[9]
        else:
            times[entry[1]] = [entry[5], entry[6], entry[7], entry[8], entry[9]]

    # Write aggregated data to CSV, getting additional place data from places_dict
    for place_id, time_data in times.items():
        if place_id in places_dict:  # Ensure place_id exists in places_dict
            places_data = places_dict[place_id]
            output.append(
                [
                    place_id,
                    places_data[0],
                    places_data[1],
                    places_data[2],
                    places_data[3],
                    *time_data,
                ]
            )
    if out.csv:
        firefoxWriter.write_csv("metadata", output)
    if out.json:
        firefoxWriter.write_json("metadata", output)
    if out.html:
        firefoxWriter.write_html("metadata", output)


def parse_logins(database: str):
    if os.path.exists(database):
        data = json.load(open(f"{database}", "r"))
        output = []
        output.append(["hostname", "formSubmitUrl", "timeCreated", "timeLastUsed", "timePasswordChanged", "timesUsed"])
        # We don't decrypt the passwords. That's getting too close to being malicious, and there is no reason to do so.
        for login in data.get("logins"):
            output.append([login.get("hostname", "No hostname specified"),
                           login.get("formSubmitURL", "No submit URL specified"),
                           convert_firefox_time(login.get("timeCreated", 0)),
                           convert_firefox_time(login.get("timeLastUsed", 0)),
                           convert_firefox_time(login.get("timePasswordChanged", 0)),
                           login.get("timesUsed", "No times used specified")
                           ])
        if out.csv:
            firefoxWriter.write_csv("logins", output)
        if out.json:
            firefoxWriter.write_json("logins", output)
        if out.html:
            firefoxWriter.write_html("logins", output)


def parse_downloads(database: str, places_dict: dict):
    # Parse downloads in firefox
    connection = connect_database(database)
    if not connection:
        return None
    try:
        cursor = connection.execute("SELECT * FROM moz_annos")
        entries = cursor.fetchall()
    except Exception as e:
        print(e)
        return 0
    entries.sort(key=itemgetter(1))
    output = []
    # Write names of fields
    output.append(["places_id", "filename", "download_url", "endTime", "size", "deleted", "canceled"])
    # Grouping the entries in downloads with those in places.sqlite. With this, we can correlate activity using the "places_id", to get url's, etc.
    for key, group in groupby(entries, key=itemgetter(1)):
        for item in group:
            if item[2] == 2 or item[2] == 1:
                if not item[3].startswith("file:"):  # We're not interested in the file:// entries, they dont have enough metadata to be useful.
                    json_data = json.loads(item[3])
                    output.append([key,
                                   places_dict.get(key)[1],
                                   places_dict.get(key)[0],
                                   convert_firefox_time(json_data.get("endTime")),
                                   json_data.get("fileSize"),
                                   json_data.get("deleted"),
                                   bool(json_data.get("state"))])
    # Write uo output, either CSV or JSON
    if out.csv:
        firefoxWriter.write_csv("downloads", output)
    if out.json:
        firefoxWriter.write_json("downloads", output)
    if out.html:
        firefoxWriter.write_html("downloads", output)


def parse_notifications(database: str):
    if os.path.exists(database):
        # Load json
        output = []
        with open(f"{database}", "r") as f:
            notificationstore = json.loads(f.read())
        output.append(["site", "id", "title", "body", "icon", "alertName", "timestamp", "origin", "mozbehavior"])
        # Look through the items in the notificationstore.json file
        for site, notifications in notificationstore.items():
            for _, notification in notifications.items():
                output.append([site,
                               notification.get("id", "No id specified"),
                               notification.get("title", "No title specified"),
                               notification.get("body", "No body specified"),
                               notification.get("icon", "No icon specified"),
                               notification.get("alertName", "No alert name specified"),
                               convert_firefox_time(notification.get("timestamp", "0")),
                               notification.get("origin", "No origin specified"),
                               notification.get("mozbehavior", "No behaviour specified")
                               ])
        if out.csv:
            firefoxWriter.write_csv("notifications", output)
        if out.json:
            firefoxWriter.write_json("notifications", output)
        if out.html:
            firefoxWriter.write_html("notifications", output)
