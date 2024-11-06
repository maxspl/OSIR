from ..log.logger_config import AppLogger
from ..utils.BaseModule import BaseModule

logger = AppLogger(__name__).get_logger()

    
class ProcessorJob:
    """
    Manages the configuration and validation of processing modules based on a specified profile and user inputs.
    """
    def __init__(self, case_path, profile, selected_modules, modules_to_add, modules_to_remove):
        """
        Initializes the ProcessorJob with details about the case, profile, and module adjustments.

        Args:
            case_path (str): The directory path where the case files are located.
            profile: The profile object containing initial configurations and modules.
            selected_modules (list): List of modules explicitly selected to run, overriding the profile.
            modules_to_add (list): Modules to add to the profile's default list.
            modules_to_remove (list): Modules to remove from the profile's default list.
        """
        self.case_path = case_path
        self.profile = profile
        self.selected_modules = selected_modules
        self.modules_to_add = modules_to_add
        self.modules_to_remove = modules_to_remove
        self.modules_selected = self._get_modules_selected()  # Final modules list
        self.module_instances = [BaseModule(self.module_selected) for self.module_selected in self.modules_selected]  # Tranform list of str to list of module
        self._validate_modules_configs()
            
    def _get_modules_selected(self):
        """
        Calculates the final list of modules to be used based on the profile and any modifications specified.

        Returns:
            list: A list of module names formatted as required for further processing.
        """
        # Initialize module list from profile
        if self.profile:
            modules = self.profile._modules_str
            modules = [item + ".yml" if not item.endswith(".yml") else item for item in modules]
        else:
            modules = []
        # Adjust module lists based on command-line options
        if self.selected_modules != []:
            # If specific modules are provided, override the profile's module list
            modules = self.selected_modules
        if self.modules_to_add != [] or self.modules_to_remove != []:
            # If modules are to be added or removed, modify the profile's module list
            test = set(modules + self.modules_to_add)
            logger.debug(f"List of module to ADD+Module: {test}")

            modules = list(set(modules + self.modules_to_add) - set(self.modules_to_remove))
        # Assuming modules list is now correctly formatted and modified
        logger.debug(f"Final list of modules: {modules}")
        logger.debug(f"List of module to ADD: {self.modules_to_add}")
        logger.debug(f"List of module to REMOVE: {self.modules_to_remove}")

        return modules 

    def _validate_modules_configs(self):
        """
        Validates the configurations of all selected modules, checking their existence, operating system compatibility, and requirements.
        
        Raises:
            SystemExit: If any validation checks fail, indicating critical errors in module configuration.
        """
        # Validate config file path
        for module_instance in self.module_instances:
            if not module_instance._module_filepath:
                logger.error(f"Selected module {module_instance.filename} is not found in configs.")
                exit()

        # Validate os
        os_values = set()
        for module_instance in self.module_instances:
            os_values.add(module_instance.get_os())

        if len(os_values) == 1 or "all" in os_values:
            logger.debug("All module instances have the same OS.")
        else:
            logger.error("Modules instances have different OS. Please check configuration.")       
            exit()