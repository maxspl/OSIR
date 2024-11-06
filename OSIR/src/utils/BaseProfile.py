from typing import Any
import yaml
import os
from src.utils.BaseModule import BaseModule
from ..log.logger_config import AppLogger
 
logger = AppLogger(__name__).get_logger()


# version: 1.0
# Author:
# Description:
# Os: windows
# Modules:
#   - extract_orc.yml
#   - evtx_orc.yml
#   - test_process_dir
#   - test_process_dir_multiple_output
#   - prefetch_orc

class BaseProfile():
    """
    Represents a profile configuration which encompasses multiple modules, potentially with varying requirements and configurations.
    """
    def __init__(self, profile_name: str) -> None:
        """
        Initializes a profile by loading its configuration from a YAML file and setting up its modules.

        Args:
            profile_name (str): The name of the profile to load.

        Raises:
            FileNotFoundError: If the profile file does not exist.
        """
        self._filename = profile_name if profile_name.endswith('.yml') else profile_name + '.yml'
        
        directory = os.path.dirname(__file__)  # Gets the directory of the current script
        relative_path = os.path.join(directory, '..', '..', 'configs', 'profiles')
        self._filepath = os.path.join(relative_path, self._filename)
        data: dict = self.get_data()

        if os.path.exists(self._filepath):
            self._version: str = data.get('version', 'Unknown version')
            self._author: str = data.get('author', 'Unknown author')
            self._description: str = data.get('description', 'No description available')
            self._os: str = data.get('os', 'Unknown OS')
            self._modules: list[BaseModule] = [BaseModule(module_name) for module_name in data['modules']] or []
            self._modules_str: list[str] = data['modules']
        else:
            raise FileNotFoundError(f"No profile found with name {self._filename} in directory {self._filepath}")

    def get_data(self) -> Any:
        """
        Loads the profile data from a YAML file.

        Returns:
            dict: The data loaded from the YAML file.

        Raises:
            Exception: If the file could not be loaded.
        """
        try: 
            return yaml.load(open(self._filepath), Loader=yaml.FullLoader)
        except Exception as e:
            logger.error("Failed to load module. Error: " + str(e))

    def validate_modules_configs(self):
        """
        Validates the configurations of all modules included in the profile. Checks include verifying file paths,
        operating system compatibility, and requirement fulfillment among the modules.

        Raises:
            SystemExit: If any validation checks fail.
        """
        # Validate config file path
        for module_instance in self._modules:
            if not module_instance._filepath:
                logger.error(f"Selected module {module_instance._filename} is not found in configs.")
                exit()

        # Validate os
        os_values = set()
        for module_instance in self._modules:
            os_values.add(module_instance._os)

        if len(os_values) == 1 or "all" in os_values:
            logger.debug("All module instances have the same OS.")
        else:
            logger.error("Modules instances have different OS. Please check configuration.")       
            exit()
    
        # Validate requirements
        modules_selected = [mod._module_name for mod in self._modules]

        for module_instance in self._modules:
            modules_required = module_instance._requirements
            if isinstance(modules_required, str):
                if modules_required in modules_selected:
                    logger.debug(f'requirement {modules_required} of module {module_instance._filename} is found')
                else:
                    logger.error(f"requirement {modules_required} of module {module_instance._filename} not found")
                    exit()
            elif isinstance(modules_required, list) and modules_required != []:
                for module_required in modules_required:
                    if module_required in modules_selected:
                        logger.debug(f'requirement {module_required} of module {module_instance._filename} is found.')
                    else:
                        print(modules_selected)
                        print(self._modules)
                        for mod in self._modules:
                            print(mod)
                        logger.error(f"requirement {module_required} of module {module_instance._filename} not found")
                        exit()
