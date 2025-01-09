import os
import shutil
import random
import string
import subprocess
import requests
from pathlib import Path
import argparse
import logging


# Function to download a file
def download_file(url, dest_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(dest_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)


# Function to replace text in a file
def replace_text_in_file(file_path, target, replacement):
    with open(file_path, 'r') as file:
        content = file.read()
    content = content.replace(target, replacement)
    with open(file_path, 'w') as file:
        file.write(content)


# Function to generate a random string
def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# Function to get the latest DFIR-Orc release download URL
def get_latest_release_url():
    api_url = "https://api.github.com/repos/DFIR-ORC/dfir-orc/releases/latest"
    response = requests.get(api_url)
    response.raise_for_status()
    release_data = response.json()
    for asset in release_data.get("assets", []):
        if asset["name"] == "DFIR-Orc_x64.exe":
            return asset["browser_download_url"]
    raise ValueError("DFIR-Orc_x64.exe not found in the latest release assets.")


def setup_logging(output_dir, input_file):
    input_file_name = Path(input_file).stem
    output_path = Path(output_dir) / input_file_name
    output_path.mkdir(parents=True, exist_ok=True)
    log_file_path = output_path / f"{input_file_name}-dfir_orc_offline.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
        ]
    )

    return log_file_path, output_path


def main():
    parser = argparse.ArgumentParser(description="Process a Windows disk image using DFIR-Orc.")
    parser.add_argument("-i", "--input", required=True, help="Path of the Windows disk image to process.")
    parser.add_argument("-o", "--output", required=True, help="Output directory to put the result.")
    parser.add_argument("-e", "--endpoint", default="unknown", help="Optional endpoint name.")

    args = parser.parse_args()

    input_path = args.input
    output_dir = args.output
    endpoint_name = args.endpoint

    # Set up logging and output directory
    log_file_path, output_path = setup_logging(output_dir, input_path)
    logging.info(f"Log file created at: {log_file_path}")

    # Retrieve current script path
    current_path = Path(__file__).parent

    # Check for DFIR-Orc_x64.exe
    tools_dir = current_path / "tools"
    tools_dir.mkdir(exist_ok=True)
    orc_exe_path = tools_dir / "DFIR-Orc_x64.exe"
    if not orc_exe_path.exists():
        logging.info("Downloading DFIR-Orc_x64.exe...")
        latest_release_url = get_latest_release_url()
        download_file(latest_release_url, orc_exe_path)

    # Create temporary directory
    tmp_dir_name = f"tmp-{generate_random_string()}"
    tmp_dir = current_path / tmp_dir_name
    tmp_dir.mkdir()

    try:
        # Copy config_offline directory to tmp_dir
        config_offline_src = current_path / "config_offline"
        config_offline_dest = tmp_dir / "config_offline"
        shutil.copytree(config_offline_src, config_offline_dest)

        # Modify DFIR-ORC_config.xml
        config_xml_path = config_offline_dest / "DFIR-ORC_config.xml"
        replace_text_in_file(config_xml_path, "{FullComputerName}", endpoint_name)

        # Modify all files in config_offline directory
        for root, _, files in os.walk(config_offline_dest):
            for file in files:
                file_path = Path(root) / file
                replace_text_in_file(file_path, "%OfflineLocation%", input_path)

        # Modify DFIR-ORC_embed.xml
        embed_xml_path = config_offline_dest / "DFIR-ORC_embed.xml"
        replace_text_in_file(embed_xml_path, ".\\%ORC_CONFIG_FOLDER%", str(config_offline_dest))
        replace_text_in_file(embed_xml_path, ".\\tools", str(tools_dir))

        # Run first subprocess command
        subprocess_command_1 = [
            str(orc_exe_path),
            "ToolEmbed",
            f"/Config={embed_xml_path}",
            f"/out={tmp_dir}\DFIR-Orc.exe"
        ]

        logging.info("Running command: %s", " ".join(subprocess_command_1))

        try:
            result_1 = subprocess.run(subprocess_command_1, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            logging.info("Processing completed successfully.")
            logging.info("Stdout: %s", result_1.stdout)
            logging.info("Stderr: %s", result_1.stderr)
            print(result_1.stdout)
            print(result_1.stderr)
        except subprocess.CalledProcessError as e:
            logging.error("Error occurred while running the command: %s", e)
            logging.error("Stdout: %s", e.stdout)
            logging.error("Stderr: %s", e.stderr)
            print(e.stdout)
            print(e.stderr)
            raise

        # Run second subprocess command
        dfir_orc_exe_path = tmp_dir / "DFIR-Orc.exe"
        subprocess_command_2 = [
            str(dfir_orc_exe_path),
            f"/Out={output_path}",
            "/Overwrite",
            f"/FullComputer={endpoint_name}"
        ]

        logging.info("Running command: %s", " ".join(subprocess_command_2))

        try:
            result_2 = subprocess.run(subprocess_command_2, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            logging.info("Processing completed successfully.")
            logging.info("Stdout: %s", result_2.stdout)
            logging.info("Stderr: %s", result_2.stderr)
            print(result_2.stdout)
            print(result_2.stderr)
        except subprocess.CalledProcessError as e:
            logging.error("Error occurred while running the command: %s", e)
            logging.error("Stdout: %s", e.stdout)
            logging.error("Stderr: %s", e.stderr)
            print(e.stdout)
            print(e.stderr)
            raise

    finally:
        # Clean up temporary directory
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
            logging.info("Temporary directory deleted: %s", tmp_dir)


if __name__ == "__main__":
    main()
