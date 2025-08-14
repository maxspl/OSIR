import os
import subprocess
import argparse
import json
import re
import base64
from symbol_builder import UbuntuSymbolsFinder

FILE_PATH = os.path.dirname(__file__)
DEFAULT_TOOLS_PATH = os.path.join(FILE_PATH, '..', 'tools')

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Find and download debug symbols for Ubuntu memory dumps."
    )
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        help="Path to the memory dump file.",
    )
   
    parser.add_argument(
        "-t",
        "--tools",
        default=DEFAULT_TOOLS_PATH,
        help="Path to the tools directory containing Volatility3 and dwarf2json.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,  # Default will be set later
        help="Directory to save the downloaded symbols.",
    )
    parser.add_argument(
        "-d", "--root-dir",
        default=os.path.join(FILE_PATH),
        help="Root directory for the script, used to locate the 'banners' directory.",
    )
    parser.add_argument(
        "-b", "--banner-dir",
        default=os.path.join(FILE_PATH, 'banners'),
        help="Path to the banners directory containing available banners and URLs to download symbols.",
    )
    parser.add_argument(
        "--force-build",
        default=False,
        action="store_true",
        help="Force the building of symbols even if present in the json symbol table files.",
    )
    args = parser.parse_args()
    
    if args.output is None:
        args.output = os.path.join(args.tools, "volatility3", "volatility3", "symbols", "linux")
    return args


def get_banners(dump_file, vol_path):
    result = subprocess.run(
        [vol_path, "-f", dump_file, "-r", "json", "banners"],
        capture_output=True,
        text=True,
        check=True,
    )

    banners_str = result.stdout
    if not banners_str:
        print("No banners found in the memory dump.")
        exit(1)

    try:
        # Parse string to list of dicts
        banners = json.loads(banners_str)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        exit(1)

    # If the folder doesn't exist, create it
    if not os.path.exists(os.path.dirname(tmp_banner_path)):
        os.makedirs(os.path.dirname(tmp_banner_path))

    with open(tmp_banner_path, "w") as f:
        json.dump(banners, f, indent=2)

    return banners

def clean_banner(banner_string):
    if banner_string.startswith("b'") and banner_string.endswith("'"):
        banner_string = banner_string[2:-1]
    return banner_string.encode('utf-8').decode('unicode_escape').strip('\x00').strip()

def update_available_symbols(vol_path, symbols_available_path):
    """
    Update the available symbols JSON file using isf plugin from volatility3.
    """
    
    if not os.path.exists(symbols_available_path):
        available_symbols = []
        # create the file if it does not exist
        with open(symbols_available_path, 'w') as f:
            json.dump(available_symbols, f, indent=4)
    else:
        with open(symbols_available_path, 'r') as f:
            try:
                available_symbols = json.load(f)
                if not isinstance(available_symbols, list):
                    available_symbols = []
            except json.JSONDecodeError:
                available_symbols = []
                print("[WARNING] except reached while reading symbols_available.json, creating a new one.")

    result = subprocess.run(
        [vol_path, "-r", "json", "isf"],
        capture_output=True,
        text=True,
        check=True,
    )
    isf_output = result.stdout

    isf_to_json = json.loads(isf_output)
    # Decode b'Linux version 6.11.0-17-generic (buildd@lcy02-amd64-038) (x86_64-linux-gnu-gcc-13 (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0, GNU ld (GNU Binutils for Ubuntu) 2.42) #17~24.04.2-Ubuntu SMP PREEMPT_DYNAMIC Mon Jan 20 22:48:29 UTC 2 (Ubuntu 6.11.0-17.17~24.04.2-generic 6.11.11)\\n\\x00' from Identifying information
    for i,entry in enumerate(isf_to_json):
        entry["index"] = i
        entry["Identifying information"] = clean_banner(entry["Identifying information"])
        
        version_short, version_extended, arch = banner_infos(entry["Identifying information"])
        entry["version_short"] = version_short
        entry["version_extended"] = version_extended
        entry["arch"] = arch
        if not check_symbol_availability(version_short, version_extended, arch):
            available_symbols.append(entry)

    with open(symbols_available_path, 'w') as f:
        json.dump(available_symbols, f, indent=4)


def banner_infos(banner: str):
    try:
        version_short, version_extended = re.findall(
            "Linux version (\\d+\\.\\d+\\.\\d+-\\d+-\\S+).+\\(Ubuntu (\\d+\\.\\d+\\.\\d+-\\d+.\\S+)-\\S+.+\\)$",
            banner,
        )[0]
        if "amd64" in banner:
            arch = "amd64"
        elif "arm64" in banner:
            arch = "arm64"
        else:
            arch = "i386"
    except:
        print(
            'Cannot parse banner, verify its validity, by running the "banners" Volatility3 plugin.'
        )
        exit(1)
    return version_short, version_extended, arch



def search_banner_in_json(json_data, banner, match_threshold=0.9):
    """
    Search for a banner in a JSON object where keys are base64-encoded banners.
    
    Args:
        json_data (dict): Parsed JSON data.
        banner (str): The original banner string to search for.
        match_threshold (float): Percentage of the base64 string to use for matching.
    
    Returns:
        list: URLs associated with the matched banner, or empty list if none found.
    """
    if "linux" not in json_data:
        print("Invalid JSON structure: 'linux' key not found.")
        return []

    encoded_banner = base64.b64encode(banner.encode()).decode()
    cutoff_len = int(len(encoded_banner) * match_threshold)

    for key in json_data["linux"]:
        if key[:cutoff_len] == encoded_banner[:cutoff_len]:
            return json_data["linux"][key]

    return []  # No match


def download_symbol(download_url:str, download_dir:str)->bool:
    """
    Download the symbol from the URL and put it in the downloaded path.
    """
    banner_name = download_url.split('/')[-1]
    # Download
    return_code = subprocess.run(
        ["wget", download_url, "-P", download_dir]
    )
    if return_code.returncode != 0:
        print(f"[ERROR] Failed to download symbol from {download_url}")
        return False
    print(f"[INFO] Successfully downloaded symbol: {banner_name}")
    return True



def check_symbol_availability(version_short: str, version_extended: str, arch: str) -> bool:
    """
    Check if the symbol has already been downloaded.
    Returns True if found, else False.
    """
    try:
        with open(symbols_available_path, "r") as f:
            available_symbols = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return False

    for symbol in available_symbols:
        if (
            symbol.get("version_short") == version_short and
            symbol.get("version_extended") == version_extended and
            symbol.get("arch") == arch
        ):
            return True
    return False

if __name__ == "__main__":
    args = parse_arguments()
    dump_file = args.file
    vol_path = os.path.join(args.tools, "volatility3", "vol.py")
    tmp_banner_path = os.path.join(args.banner_dir, "tmp", "tmp_banners.json")
    all_banners_file_path = os.path.join(args.banner_dir, "all_banners.json")
    symbols_available_path = os.path.join(args.banner_dir, "symbols_available.json")

    # Step 1 Grab all banners
    print("Searching for symbols using volatility banner's plugin...")
    banners = get_banners(dump_file, vol_path)
    print(f"[INFO] Updating available symbols from {vol_path} using isf plugin...")
    update_available_symbols(vol_path, symbols_available_path)
    # Test if the banner is already available

    # Step 2: If a banner is found, search the URL to download it
    if banners:
        if not args.force_build:
            with open(all_banners_file_path, "r") as f:
                symbol_json = json.load(f)
            for banner in banners:
                infos = banner_infos(banner["Banner"])
                # Check if the symbol is not already available
                if check_symbol_availability(infos[0], infos[1], infos[2]):
                    print(f"[INFO] Symbol already available for {infos[0]} ({infos[1]}) {infos[2]}, skipping")
                    exit(0)
                match_urls = search_banner_in_json(symbol_json, banner["Banner"], 0.8)
                if match_urls:
                    download_url = match_urls[0]
                    infos = banner_infos(banner["Banner"])
                    # Check if the symbol is not already available 
                    if not check_symbol_availability(infos[0], infos[1], infos[2]):
                        download_symbol(download_url, args.output)
                        print(f"[INFO] Downloaded symbol for {infos[0]} ({infos[1]}) {infos[2]} from {download_url}")
                        update_available_symbols(vol_path, symbols_available_path)
                    else:
                        print(f"[INFO] Symbol already available, skipping")
                    exit(0)
        # Try to build the banner from the file name
            print(f"[INFO] No banners corresponding in 'all_banners' json table. Trying to build banner from a kernel build")
        with open(tmp_banner_path, "r") as f:
            banners = json.load(f)
            for banner in banners:
                print(f"[INFO] Trying to build banner from {banner['Banner']}")
                finder = UbuntuSymbolsFinder(banner["Banner"], args.tools, args.banner_dir)
                try:
                    completed = finder.run()
                    if completed:
                        update_available_symbols(vol_path, symbols_available_path)
                        print(f"[INFO] Successfully added symbols for {finder.version_short} ({finder.version_extended}) {finder.arch}")
                        exit(0)
                except ValueError as e:
                    print(f"[ERROR] {e}")
