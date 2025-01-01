from datetime import datetime, timedelta
import sqlite3
import os
import json
import plyvel  # type: ignore
from lib.a_pb2 import NotificationDatabaseDataProto  # type: ignore
from lib.output import outputWriter  # type: ignore


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


def convert_time(timestamp):
    """Convert Chromium timestamp to standard datetime format."""
    chromium_base_date = datetime(1601, 1, 1)
    timestamp_delta = timedelta(microseconds=timestamp)
    return str(chromium_base_date + timestamp_delta)


def parse_downloads(database):
    """Parse downloads data from the SQLite database and save it to a CSV file."""
    connection = connect_database(database)
    if not connection:
        return None
    try:
        cursor = connection.execute("SELECT * FROM downloads")
        entries = cursor.fetchall()
    except Exception as e:
        print(e)
        return 0
    output = []
    output.append(
            [
                "filename",
                "current_path",
                "target_path",
                "start_time",
                "received_bytes",
                "total_bytes",
                "end_time",
                "opened",
                "last_access_time",
                "mime_type",
            ]
        )

    for entry in entries:
        filename = entry[2].split("\\")[-1]
        output.append(
            [
                filename,
                entry[2],
                entry[3],
                convert_time(entry[4]),
                entry[5],
                entry[6],
                convert_time(entry[11]),
                str(bool(entry[12])),
                convert_time(entry[13]),
                entry[25],
            ]
            )
    if out.csv:
        operaWriter.write_csv("downloads", output)
    if out.json:
        operaWriter.write_json("downloads", output)
    if out.html:
        operaWriter.write_html("downloads", output)


def parse_history(database):
    """Parse browsing history data from the SQLite database and save it to a CSV file."""
    connection = connect_database(database)
    if not connection:
        return None
    try:
        cursor = connection.execute("SELECT * FROM urls")
        entries = cursor.fetchall()
    except Exception as e:
        print(e)
        return 0
    output = []
    output.append(["url", "title", "visit_count", "last_visit_time"])

    for entry in entries:
        title = (
            entry[2]
            if not entry[1].startswith("file://")
            else entry[1].split("/")[-1]
        )
        output.append([entry[1], title, entry[3], convert_time(entry[5])])
    if out.csv:
        operaWriter.write_csv("history", output)
    if out.json:
        operaWriter.write_json("history", output)
    if out.html:
        operaWriter.write_html("history", output)


def parse_visited_links(database):
    """Parse visited links data from the SQLite database and save it to a CSV file."""
    connection = connect_database(database)
    if not connection:
        return None
    try:
        cursor = connection.execute("SELECT * FROM visited_links")
        entries = cursor.fetchall()
    except Exception as e:
        print(e)
        return 0
    output = []
    output.append(["top_level_url", "frame_url", "visit_count"])

    for entry in entries:
        output.append([entry[2], entry[3], entry[4]])
    if out.csv:
        operaWriter.write_csv("visited_links", output)
    if out.json:
        operaWriter.write_json("visited_links", output)
    if out.html:
        operaWriter.write_html("visited_links", output)


def parse_searches(database):
    """Parse search terms data from the SQLite database and save it to a CSV file."""
    connection = connect_database(database)
    if not connection:
        return None
    try:
        cursor = connection.execute("SELECT * FROM keyword_search_terms")
        entries = cursor.fetchall()
    except Exception as e:
        print(e)
        return 0
    output = []
    output.append(["term", "normalized_term"])

    for entry in entries:
        output.append([entry[2], entry[3]])
    if out.csv:
        operaWriter.write_csv("searches", output)
    if out.json:
        operaWriter.write_json("searches", output)
    if out.html:
        operaWriter.write_html("searches", output)


def parse_favicons(database):
    """Parse favicons data from the SQLite database and save it to a CSV file."""
    connection = connect_database(database)
    if not connection:
        return None
    try:
        cursor = connection.execute("SELECT * FROM favicons")
        entries = cursor.fetchall()
    except Exception as e:
        print(e)
        return 0
    output = []
    output.append(["url"])
    for entry in entries:
        output.append([entry[1]])
    if out.csv:
        operaWriter.write_csv("favicons", output)
    if out.json:
        operaWriter.write_json("favicons", output)
    if out.html:
        operaWriter.write_html("favicons", output)


def parse_cookies(database):
    """Parse cookies from the SQLite database and save it to a CSV file"""

    connection = connect_database(database)
    if not connection:
        return None
    try:
        cursor = connection.execute("SELECT * FROM cookies")
        entries = cursor.fetchall()
    except Exception as e:
        print(e)
        return 0
    output = []
    output.append(
        [
            "created_utc",
            "host_key",
            "name",
            "value",
            "expires_utc",
            "last_access_utc",
            "source_port",
            "last_update_utc",
        ]
        )
    for entry in entries:
        output.append(
            [
                convert_time(entry[0]),
                entry[1],
                entry[3],
                entry[4],
                convert_time(entry[7]),
                convert_time(entry[10]),
                entry[16],
                convert_time(entry[17]),
            ]
        )
    if out.csv:
        operaWriter.write_csv("cookies", output)
    if out.json:
        operaWriter.write_json("cookies", output)
    if out.html:
        operaWriter.write_html("cookies", output)


def parse_shortcuts(database):
    """Parse shortcuts from the SQLite database and save it to a CSV file"""

    connection = connect_database(database)
    if not connection:
        return None
    try:
        cursor = connection.execute("SELECT * FROM omni_box_shortcuts")
        entries = cursor.fetchall()
    except Exception as e:
        print(e)
        return 0
    output = []
    output.append(
        [
            "text",
            "fill_into_edit",
            "contents",
            "keyword",
            "last_access_time",
            "number_of_hits",
        ]
    )
    for entry in entries:
        output.append(
            [
                entry[1],
                entry[2],
                entry[5],
                entry[11],
                convert_time(entry[12]),
                entry[13],
            ]
        )
    if out.csv:
        operaWriter.write_csv("shortcuts", output)
    if out.json:
        operaWriter.write_json("shortcuts", output)
    if out.html:
        operaWriter.write_html("shortcuts", output)


def parse_chromium_notifications(database):
    class ClosedReason:
        USER = "0"
        DEVELOPER = "1"
        UNKNOWN = "2"

    # Found in chromium source-code (https://source.chromium.org/chromium/chromium/src/+/main:content/browser/notifications/notification_database_data.proto) Line 16-20
    map_field_to_reason = {
        ClosedReason.USER: "USER",
        ClosedReason.DEVELOPER: "DEVELOPER",
        ClosedReason.UNKNOWN: "UKNOWN"
    }

    db_path = database
    if os.path.exists(f"{database}"):
        # Stupid fix
        if len(os.listdir(database)) < 4:
            return None
        try:
            db = plyvel.DB(db_path, create_if_missing=False)
            output = []
            output.append(["title", "lang", "body", "tag", "icon", "is_silent", "require_interaction", "time", "badge", "image", "numClicks", "creation_time_millis", "closed_reason", "has_triggered", "origin"])
            for key, value in db:
                data = value

                # Create an instance of the generated class and parse the data.
                notification_data = NotificationDatabaseDataProto()
                notification_data.ParseFromString(data)
                output.append([notification_data.notification_data.title,
                               notification_data.notification_data.lang,
                               notification_data.notification_data.body,
                               notification_data.notification_data.tag,
                               notification_data.notification_data.icon,
                               notification_data.notification_data.silent,
                               notification_data.notification_data.require_interaction,
                               convert_time(int(notification_data.notification_data.timestamp)),
                               notification_data.notification_data.badge,
                               notification_data.notification_data.image,
                               notification_data.num_clicks,
                               notification_data.creation_time_millis,
                               map_field_to_reason.get(str(notification_data.closed_reason)),
                               notification_data.has_triggered,
                               notification_data.origin
                               ])
            if out.csv:
                operaWriter.write_csv("notifications", output)
            if out.json:
                operaWriter.write_json("notifications", output)
            if out.html:
                operaWriter.write_html("notifications", output)
        except Exception as e:
            print(e)


def parse_extensions(path):
    if not os.path.exists(path):
        return None
    output = []
    output.append(["name", "author", "version", "description", "developer"])
    for extension in os.listdir(path):
        id = os.listdir(f"{path}/{extension}")[0]
        f = open(f"{path}/{extension}/{id}/manifest.json", "r")
        manifest = json.loads(f.read())
        try:
            output.append([manifest.get("name", "No name specified"), manifest.get("author", "No author specified"), manifest.get("manifest_version", "No version specified"), manifest.get("description", "No description specified"), manifest.get("developer", "No developer specified")])
        except KeyError:
            print(f"[!] Error parsing {operaWriter.browser} extensions, check them manually!")
    if out.csv:
        operaWriter.write_csv("extensions", output)
    if out.json:
        operaWriter.write_json("extensions", output)
    if out.html:
        operaWriter.write_html("extensions", output)


def parse_opera_data(user, directory, output, args):
    print("[*] Starting to parse Opera")
    global out
    out = args
    global operaWriter
    operaWriter = outputWriter(output, user, "opera")
    parse_downloads(f"{directory}/History")
    parse_history(f"{directory}/History")
    parse_visited_links(f"{directory}/History")
    parse_searches(f"{directory}/History")
    parse_favicons(f"{directory}/Favicons")
    parse_cookies(f"{directory}/Network/Cookies")
    parse_shortcuts(f"{directory}/Shortcuts")
    parse_chromium_notifications(f"{directory}/Platform Notifications")
    parse_extensions(f"{directory}/Extensions")
