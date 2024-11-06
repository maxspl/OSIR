#!/usr/bin/env python
import argparse
import sys
import threading
import os
import src.tasks.task_manager as task_manager
import src.tasks.tasks as tasks
from src.log.logger_config import AppLogger
import src.monitor.MonitorCase as MonitorCase
import src.utils.SmbMounter as SmbMounter
import src.utils.BaseProfile as BaseProfile
from streamlit.web import cli

logger = AppLogger(__name__).get_logger()


def comma_separated_strings(value):
    """
    Converts a comma-separated string into a list of strings, ensuring each item has a '.yml' extension.

    Args:
        value (str): Comma-separated string input from command line arguments.

    Returns:
        list: A list of strings, each potentially modified to end with '.yml'.
    """
    if not value:
        return []
    items = [item.strip() for item in value.split(',')]
    items_with_yml = [item + ".yml" if not item.endswith(".yml") else item for item in items]
    return items_with_yml


def parse_args():
    """
    Parses command line arguments to configure the processing environment and tasks.

    Returns:
        argparse.Namespace: Namespace object containing the parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description='Process configuration files.')
    parser.add_argument('--profile', type=str, help='Name of the profile, with or without the .yml extension.')
    parser.add_argument('--module', type=comma_separated_strings, default=[], help='Set a specific list of modules to be exclusively used.')
    parser.add_argument('--module_add', type=comma_separated_strings, default=[], help='Add specific modules to the list.')
    parser.add_argument('--module_remove', type=comma_separated_strings, default=[], help='Remove specific modules from the list.')
    parser.add_argument('--agent', action='store_true', help='Launch the agent and wait for processing tasks from master.')
    parser.add_argument('--case', type=str, help='Name of the case in /OSIR/share/cases directory.')
    parser.add_argument('--web', action='store_true', help='Launch the web app.')

    args = parser.parse_args() 
    
    # Check if at least on arg is provided --profile or --module or --agent or --web
    if len(sys.argv) == 1:
        # Print help message and exit if no arguments were given.
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    # Check if module_add or module_remove is used without profile
    if (args.module_add or args.module_remove) and not args.profile:
        logger.error("--module_add or --module_remove can only be used when a --profile is specified.")
        sys.exit(1)
        
    # Ensure --agent is used alone if used
    if args.agent:
        if args.profile or args.module or args.module_add or args.module_remove or args.case or args.web:
            logger.error("--agent can only be used alone.")
            sys.exit(1)
            
    # Check if --case is used with --profile or --module
    if (args.profile or args.module) and not args.case:
        logger.error("--case must be set when using --profile or --module.")
        sys.exit(1)
        
    return args


def main():
    """
    Main function that sets up and launches the monitoring and processing tasks based on command line arguments.
    This function orchestrates the entire process, from parsing arguments to setting up monitoring for case files
    and potentially starting Celery workers if running in agent mode.
    """
    args = parse_args()
    
    # If agent mode
    if args.agent:
        logger.info("agent option has been selected. Workers will be launched and Samba share mounted if master is remote...")
        mounter = SmbMounter.SMBMounter("/OSIR/share/", "guest", "")
        if not mounter.standalone:
            logger.info("master is remote, mounting samba share...")
            mounter.mount()
            mounter.start_monitoring()  # Start a thread to monitor smb access

        worker = tasks.CeleryWorker()
        worker.start_worker()
    
    if args.web:
        logger.info("Launching web app...")
        cli.main_run(["/OSIR/OSIR/src/web_app/⚡_Processor.py"])

    case_path = os.path.join("/OSIR/share/cases", args.case)
    if not os.path.isdir(case_path):
        logger.error(f"You selected a case that does not exist. Verify that {case_path} is the right path to process")
        exit()
        
    # Create an instance of the profile class
    # profile_instance = task_manager.profile(args.profile) if args.profile else None
    profile_instance = BaseProfile.BaseProfile(args.profile) if args.profile else None
    
    # Initialize module lists based on command-line arguments
    selected_modules = args.module if args.module else []
    modules_to_add = args.module_add if args.module_add else []
    modules_to_remove = args.module_remove if args.module_remove else []
    
    # Get the modules to process
    job = task_manager.ProcessorJob(case_path, profile_instance, selected_modules, modules_to_add, modules_to_remove)
    modules = job._get_modules_selected()
    
    monitor_case = MonitorCase.MonitorCase(case_path, modules)

    # Start monitoring the case directory  in a separate thread
    setup_thread = threading.Thread(target=monitor_case.setup_handler)
    setup_thread.start()

    # Wait for the _setup_handler() thread to finish before exiting the code
    try:
        # Wait for the _setup_handler() thread to finish before exiting the code
        setup_thread.join()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Stopping...")
        monitor_case.stop_event.set()
        setup_thread.join()
    
    
if __name__ == "__main__":    
    main()
