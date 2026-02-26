import argparse
from dotenv import load_dotenv
import os
from osir_client.client.OsirClient import OsirClient
from osir_lib.logger.logger import CustomLogger
from osir_lib.logger import AppLogger
from osir_client.client.OsirCliDisplay import OsirCliDisplay

load_dotenv()

logger: CustomLogger = AppLogger().get_logger()

DEFAULT_API_URL = os.getenv("OSIR_API_URL")


def main():
    parser = argparse.ArgumentParser(description="Command-line tool to interact with the OSIR API.")

    # Global - now optional if set in .env
    parser.add_argument(
        "-u", "--api-url",
        default=DEFAULT_API_URL,
        help="OSIR API URL (e.g., http://127.0.0.1:8502). Can also be set via OSIR_API_URL in .env"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- CASE ---
    case_parser = subparsers.add_parser("case", help="Manage cases")
    case_sub = case_parser.add_subparsers(dest="action", required=True)

    case_sub.add_parser("list", help="List all cases")

    case_create = case_sub.add_parser("create", help="Create a new case")
    case_create.add_argument("-c", "--case-name", required=True, help="Name of the case to create")

    # --- MODULE ---
    module_parser = subparsers.add_parser("module", help="Manage and run modules")
    module_sub = module_parser.add_subparsers(dest="action", required=True)

    module_sub.add_parser("list", help="List all available modules")

    module_list_cat = module_sub.add_parser("list-category", help="List modules for a specific category")
    module_list_cat.add_argument("-cat", "--category", required=True, help="Category (e.g., windows, unix, splunk)")
    module_list_cat.add_argument("-sub", "--subcategory", required=False, help="Subcategory (e.g., live_response, dissect)")
    module_list_cat.add_argument("-subsub", "--subsubcategory", required=False, help="Sub-subcategory (e.g., packages, storage, process, network, hardware, system)")

    module_exists = module_sub.add_parser("exists", help="Check if a module exists")
    module_exists.add_argument("-m", "--module-name", required=True, help="Module name to check")

    module_run = module_sub.add_parser("run", help="Run a module against a case")
    module_run.add_argument("-c", "--case-name", required=True, help="Case name")
    module_run.add_argument("-m", "--module-name", required=True, help="Module file to run (e.g., bodyfile.yml)")
    module_run.add_argument("-i", "--input-path", required=False, help="Optional path to input file to upload.")
    module_run.add_argument("-w", "--wait", action="store_true", help="Wait for completion")

    # --- PROFILE ---
    profile_parser = subparsers.add_parser("profile", help="Manage and run profiles")
    profile_sub = profile_parser.add_subparsers(dest="action", required=True)

    profile_sub.add_parser("list", help="List all available profiles")

    profile_exists = profile_sub.add_parser("exists", help="Check if a profile exists")
    profile_exists.add_argument("-p", "--profile-name", required=True, help="Profile name to check")

    profile_run = profile_sub.add_parser("run", help="Run a profile against a case")
    profile_run.add_argument("-c", "--case-name", required=True, help="Case name")
    profile_run.add_argument("-p", "--profile-name", required=True, help="Profile name to run")
    profile_run.add_argument("-w", "--wait", action="store_true", help="Wait for completion")

    # --- HANDLER ---
    handler_parser = subparsers.add_parser("handler", help="Manage handlers")
    handler_sub = handler_parser.add_subparsers(dest="action", required=True)

    handler_list = handler_sub.add_parser("list", help="List handlers for a case")
    handler_list.add_argument("-c", "--case-name", required=True, help="Case name")

    handler_status = handler_sub.add_parser("status", help="Get handler status")
    handler_status.add_argument("-i", "--handler-id", required=True, help="Handler UUID")
    handler_status.add_argument("-w", "--wait", action="store_true", help="Wait for completion")

    # --- TASK ---
    task_parser = subparsers.add_parser("task", help="Manage tasks")
    task_sub = task_parser.add_subparsers(dest="action", required=True)

    task_list = task_sub.add_parser("list", help="List all tasks")
    task_list.add_argument("-c", "--case-name", required=True, help="Case name")

    task_info = task_sub.add_parser("info", help="Get task info")
    task_info.add_argument("-i", "--task-id", required=True, help="Task UUID")

    args = parser.parse_args()

    if not args.api_url:
        parser.error("API URL is required. Set OSIR_API_URL in your .env file or use --api-url.")

    try:
        osir = OsirClient(api_url=args.api_url)

        # --- CASE ---
        if args.command == "case":
            if args.action == "list":
                osir.cases.list()

            elif args.action == "create":
                case = osir.cases.create(args.case_name)
                logger.info(f"Case '{case.name}' created with UUID: {case.case_uuid}")

        # --- MODULE ---
        elif args.command == "module":
            if args.action == "list":
                osir.cases.modules.list()

            elif args.action == "list-category":
                tree = osir.cases.modules.list(print=False)

                category = args.category
                subcategory = getattr(args, "subcategory", None)
                subsubcategory = getattr(args, "subsubcategory", None)

                group = getattr(tree, category, None)
                if group is None:
                    logger.error(f"Category '{category}' not found. Available: windows, unix, splunk, scan, network, pre_process, test")
                    return

                if subcategory:
                    group = getattr(group, subcategory, None)
                    if group is None:
                        logger.error(f"Subcategory '{subcategory}' not found in '{category}'. Available: live_response, dissect")
                        return

                    if subsubcategory:
                        group = getattr(group, subsubcategory, None)
                        if group is None:
                            logger.error(f"Sub-subcategory '{subsubcategory}' not found. Available: packages, storage, process, network, hardware, system")
                            return

                OsirCliDisplay.modules_flat(group.modules, category, subcategory, subsubcategory)

            elif args.action == "exists":
                module = osir.cases.modules.exists(args.module_name)
                logger.info(f"Module info: {module}")

            elif args.action == "run":
                handler = (
                    osir.cases
                    .get(args.case_name)
                    .modules
                    .run(
                        args.module_name,
                        input_path=getattr(args, "input_path", None)
                    )
                )
                if getattr(args, "input_path", None):
                    OsirCliDisplay.task_info(handler)
                else:
                    handler.status(wait_end=args.wait)

        # --- PROFILE ---
        elif args.command == "profile":
            if args.action == "list":
                profiles = osir.cases.profiles.list()
                # logger.info(f"Available profiles: {profiles}")

            elif args.action == "exists":
                profile = osir.cases.profiles.exists(args.profile_name)
                logger.info(f"Profile info: {profile}")

            elif args.action == "run":
                handler = (
                    osir.cases
                    .get(args.case_name)
                    .profiles
                    .run(args.profile_name)
                )
                logger.info(handler)
                handler.status(wait_end=args.wait)

        # --- HANDLER ---
        elif args.command == "handler":
            if args.action == "list":
                osir.cases.get(args.case_name).handlers.list()

            elif args.action == "status":
                from osir_client.client.OsirCliHandler import OsirCliHandler
                handler = OsirCliHandler(handler_id=args.handler_id)
                handler._api = osir
                handler.status(wait_end=args.wait)

        # --- TASK ---
        elif args.command == "task":
            if args.action == "list":
                osir.cases.get(args.case_name).tasks.list()
    
            elif args.action == "info":
                task = osir.cases.tasks.get_task_info(args.task_id)
                # logger.info(f"Task info: {task}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    if not os.getenv("OSIR_HOME"):
        logger.warning("OSIR_HOME env var not set default is /OSIR !")
    main()