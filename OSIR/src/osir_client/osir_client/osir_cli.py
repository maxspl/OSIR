import argparse
from osir_client.api.osir_api_client import OsirApiClient
from osir_lib.logger.logger import CustomLogger
from osir_lib.logger import AppLogger

logger: CustomLogger = AppLogger().get_logger()


def main():

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Command-line tool to interact with the Osir API.")

    # Add arguments with short and long options
    parser.add_argument("-u", "--api-url", required=True, help="Osir API URL (e.g., http://127.0.0.1:8502)")
    parser.add_argument("-c", "--case-name", required=True, help="Name of the case (e.g., test_1)")
    parser.add_argument("-m", "--module-file", help="Module file to run (e.g., bodyfile.yml)")
    parser.add_argument("-h", "--handler-id", help="Handler ID (optional)")
    parser.add_argument("-t", "--task-id", help="Task ID (optional)")

    # Parse arguments
    args = parser.parse_args()

    try:
        # Initialize OsirApiClient
        osir_cli = OsirApiClient(api_url=args.api_url)

        # Execute the module if specified
        if args.module_file:
            result = osir_cli.cases.get(args.case_name).modules.run(args.module_file).status(wait_end=True)
            logger.info(f"Module execution completed with result: {result}")

        # Add additional actions for handlers or tasks if needed

    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
