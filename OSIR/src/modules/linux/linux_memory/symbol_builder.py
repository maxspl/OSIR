# ubuntu_symbols_finder.py
import re
import subprocess
import shutil
import os
import sys
FILE_PATH = os.path.dirname(__file__)
LIB_PATH = os.path.join(FILE_PATH, '..', 'lib')
DEFAULT_TOOLS_PATH = os.path.join(FILE_PATH, '..', 'tools')
if LIB_PATH not in sys.path:
    sys.path.insert(0, LIB_PATH)
import requests

class UbuntuSymbolsFinder:
    BASE = "https://launchpad.net/ubuntu/{release}/{arch}/linux-image-unsigned-{version_short}-dbgsym/{version_extended}"
    BASE2 = "https://launchpad.net/ubuntu/{release}/{arch}/linux-image-{version_short}-dbgsym/{version_extended}"

    def __init__(self, banner: str, tools_path: str = DEFAULT_TOOLS_PATH, banner_path: str = os.path.join(FILE_PATH, '..')):
        """
        Initialize the UbuntuSymbolsFinder with the kernel banner and tools path.
        :param banner: The kernel banner string.    
        :param tools_path: The path to the tools directory containing `dwarf2json` and `volatility3`.
        :param banner_path: The path to the temporary directory where files will be downloaded and processed.
        """
        self.banner = banner
        self.version_short = None
        self.version_extended = None
        self.arch = None
        self.download_url = None
        self.banner_path = banner_path
        self.tools_path = tools_path
        self.dwarf2json_path = os.path.join(tools_path, "dwarf2json", "dwarf2json")
        self.volatility_path = os.path.join(tools_path, "volatility3", "volatility3", "vol.py")
        self.volatility_symbols_path = os.path.join(tools_path, "volatility3", "volatility3", "symbols", "linux")

    def get_ubuntu_releases(self):
        r = requests.get("https://api.launchpad.net/devel/ubuntu/series", verify=False).json()
        return [entry["name"] for entry in r["entries"]]

    def parse_banner(self):
        try:
            self.version_short, self.version_extended = re.findall(
                r"Linux version (\d+\.\d+\.\d+-\d+-\S+).+\(Ubuntu (\d+\.\d+\.\d+-\d+\.\S+)-\S+.+\)$",
                self.banner,
            )[0]

            if "amd64" in self.banner:
                self.arch = "amd64"
            elif "arm64" in self.banner:
                self.arch = "arm64"
            else:
                self.arch = "i386"

            print(
                f"Detected version_short: {self.version_short}, version_extended: {self.version_extended}, arch: {self.arch}"
            )
        except:
            raise ValueError("Cannot parse banner. Verify its validity.")

    def search_debug_symbols(self):
        releases = self.get_ubuntu_releases()
        for base in [self.BASE, self.BASE2]:
            for release in releases:
                check_url = base.format(
                    arch=self.arch,
                    release=release,
                    version_short=self.version_short,
                    version_extended=self.version_extended,
                )
                r = requests.get(check_url, verify=False)
                if r.status_code == 200:
                    try:
                        pattern = rf'href="(http[s]?://[^"]+_{re.escape(self.version_extended)}_{self.arch}\.ddeb)"'
                        match = re.findall(pattern, r.text)
                        self.download_url = match[0] if match else None
                        print(f"Download URL found: {self.download_url}")
                        return
                    except:
                        print(
                            f"Detected URL {check_url} but download link couldn't be extracted."
                        )
        raise RuntimeError("Couldn't find debug symbols.")

    def download_and_generate_isf(self):
        ddeb_filename = self.download_url.split("/")[-1]
        ddeb_filename_no_ext = ddeb_filename.rsplit(".", 1)[0]

        tmp_dir = os.path.join(self.banner_path, "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        os.makedirs(self.volatility_symbols_path, exist_ok=True)

        ddeb_path = os.path.join(tmp_dir, ddeb_filename)
        extract_dir = os.path.join(tmp_dir, ddeb_filename_no_ext)
        isf_output_tmp = os.path.join(tmp_dir, f"{ddeb_filename_no_ext}.json")
        isf_output_final = os.path.join(self.volatility_symbols_path, f"{ddeb_filename_no_ext}.json")

        try:
            print(f"[INFO] Downloading {ddeb_filename} to {tmp_dir}...")
            subprocess.run(["wget", self.download_url, "-O", ddeb_path], check=True)
            print("[INFO] Download finished.")

            print(f"[INFO] Extracting {ddeb_filename}...")
            subprocess.run(["dpkg-deb", "-x", ddeb_path, extract_dir], check=True)
            print("[INFO] Extraction finished.")

            print(f"[INFO] Generating ISF for {self.version_short}...")
            with open(isf_output_tmp, "wb") as output_file:
                proc = subprocess.run(
                    [
                        self.dwarf2json_path,
                        "linux",
                        "--elf",
                        os.path.join(extract_dir, f"usr/lib/debug/boot/vmlinux-{self.version_short}")
                    ],
                    stdout=output_file,
                    check=True
                )

            print(f"[INFO] ISF generated at {isf_output_tmp}")

            print(f"[INFO] Moving ISF to {self.volatility_symbols_path}...")
            shutil.move(isf_output_tmp, isf_output_final)

            print(f"[INFO] ISF file available at: {isf_output_final}")
            return True
        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")
            print("[ERROR] Failed to download or process the debug symbols.")
            return False
        
        finally:
            print("[INFO] Cleaning up temporary files...")
            if os.path.exists(ddeb_path):
                os.remove(ddeb_path)
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            print("[INFO] Cleanup completed.")
    


    def run(self):
        self.parse_banner()
        self.search_debug_symbols()
        if not self.download_url:
            raise RuntimeError("Failed to find debug symbols for this kernel version.")
        return self.download_and_generate_isf()
