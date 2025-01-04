import argparse
from lib.detectBrowser import locate_browser_directories
from lib.firefox import parse_firefox_data
from lib.edge import parse_edge_data
from lib.chrome import parse_chrome_data
from lib.opera import parse_opera_data
from lib.brave import parse_brave_data
from lib.yandex import parse_yandex_data


def main(args):
    directories = locate_browser_directories(args.directory)
    output = args.output
    if output[-1] != "/":
        output += "/"
    for user in directories.keys():
        for directory in directories[user]:
            if directory == "Firefox":
                for profile in directories[user][directory]:
                    parse_firefox_data(user, profile.replace("//", "/"), profile.split("/")[-1], output, args)
                    print(f"[*] Finished parsing Firefox profile {profile.split('/')[-1]}")

            if directory == "Chrome":

                parse_chrome_data(user, directories[user][directory].replace("//", "/"), output, args)
                print("[*] Finished parsing Chrome")

            if directory == "Edge":
                parse_edge_data(user, directories[user][directory].replace("//", "/"), output, args)
                print("[*] Finished parsing Edge")

            if directory == "Opera":
                parse_opera_data(user, directories[user][directory.replace("//", "/")], output, args)
                print("[*] Finished parsing Opera")

            if directory == "Brave":
                parse_brave_data(user, directories[user][directory.replace("//", "/")], output, args)
                print("[*] Finished parsing Brave")

            if directory == "Yandex":
                parse_yandex_data(user, directories[user][directory.replace("//", "/")], output, args)
                print("[*] Finished parsing Yandex")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BrowserParser parses most of all relevant browser artifacts, from the output of KAPE")
    
    parser.add_argument("directory")
    parser.add_argument("output")

    # Create a mutually exclusive group
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--csv", action="store_true", help="Output in CSV format")
    group.add_argument("--json", action="store_true", help="Output in JSON format")
    group.add_argument("--html", action="store_true", help="Output in HTML format")
    
    # Add arguments to the group
    args = parser.parse_args()
    main(args)
    print("[*] Done parsing!")
