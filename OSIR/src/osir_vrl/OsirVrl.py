import sys
from os.path import dirname, abspath, join, isfile, isdir
import os

# Add parent directory to path so we can import osir_vrl
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from osir_vrl.osir_vrl.OsirVrlModel import OsirVrlModel


class OsirVrl:
    """Class to generate VRL configurations from YAML transform files."""
    
    DEFAULT_TRANSFORM_DIR = "/home/typ/Desktop/OSIR/OSIR/configs/dependencies/transform"
    DEFAULT_ECS_DIR = "/home/typ/Desktop/OSIR/OSIR/configs/dependencies/ecs_normalize"
    
    @classmethod
    def from_yaml(cls, yaml_path: str, vrl_path: str = None) -> "OsirVrlModel":
        """Convert a YAML file to OsirVrlModel and optionally save to VRL.
        
        Args:
            yaml_path: Path to the YAML configuration file
            vrl_path: Optional path to save the generated VRL file
            
        Returns:
            OsirVrlModel instance
        """
        model = OsirVrlModel.from_yaml(yaml_path)
        if vrl_path:
            model.save_vrl(vrl_path)
        return model
    
    @classmethod
    def _get_yaml_files(cls, directory: str) -> list[str]:
        """Recursively find all YAML files in a directory.
        
        Args:
            directory: Root directory to search
            
        Returns:
            List of paths to YAML files
        """
        yaml_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.yml') or file.endswith('.yaml'):
                    yaml_files.append(join(root, file))
        return yaml_files
    
    @classmethod
    def _yaml_to_vrl_path(cls, yaml_path: str, transform_dir: str, ecs_dir: str) -> str:
        """Convert a YAML file path to the corresponding VRL path.
        
        Preserves the directory structure relative to transform_dir.
        
        Example:
            transform_dir = /configs/dependencies/transform
            yaml_path = /configs/dependencies/transform/windows/defender.yml
            ecs_dir = /configs/dependencies/ecs_normalize
            -> /configs/dependencies/ecs_normalize/windows/defender.vrl
        
        Args:
            yaml_path: Path to the YAML file
            transform_dir: Root directory of transform configs
            ecs_dir: Root directory for ECS normalize output
            
        Returns:
            Path to the VRL file
        """
        # Get relative path from transform_dir
        rel_path = os.path.relpath(yaml_path, transform_dir)
        # Change extension from .yml/.yaml to .vrl
        vrl_rel_path = os.path.splitext(rel_path)[0] + '.vrl'
        # Join with ecs_dir
        return join(ecs_dir, vrl_rel_path)
    
    @classmethod
    def generate_from_directory(
        cls,
        transform_dir: str = None,
        ecs_dir: str = None,
        force: bool = False
    ) -> dict[str, str]:
        """Generate all VRL files from YAML files in a directory.
        
        Args:
            transform_dir: Directory containing YAML transform configs
                        (default: DEFAULT_TRANSFORM_DIR)
            ecs_dir: Directory to save VRL files
                    (default: DEFAULT_ECS_DIR)
            force: If True, overwrite existing VRL files
                    (default: False)
            
        Returns:
            Dictionary mapping YAML paths to generated VRL paths
        """
        if transform_dir is None:
            transform_dir = cls.DEFAULT_TRANSFORM_DIR
        if ecs_dir is None:
            ecs_dir = cls.DEFAULT_ECS_DIR
        
        yaml_files = cls._get_yaml_files(transform_dir)
        generated = {}
        
        for yaml_path in yaml_files:
            vrl_path = cls._yaml_to_vrl_path(yaml_path, transform_dir, ecs_dir)
            
            # Create output directory if it doesn't exist
            vrl_dir = dirname(vrl_path)
            if not isdir(vrl_dir):
                os.makedirs(vrl_dir, exist_ok=True)
            
            # Skip if VRL file exists and force is False
            if not force and isfile(vrl_path):
                print(f"Skipping {yaml_path} -> {vrl_path} (already exists)")
                continue
            
            # Convert and save
            model = OsirVrlModel.from_yaml(yaml_path)
            model.save_vrl(vrl_path)
            generated[yaml_path] = vrl_path
            print(f"Generated: {yaml_path} -> {vrl_path}")
        
        return generated
    
    @classmethod
    def generate_all(cls, force: bool = False) -> dict[str, str]:
        """Generate all VRL configurations from the default transform directory.
        
        Args:
            force: If True, overwrite existing VRL files
            
        Returns:
            Dictionary mapping YAML paths to generated VRL paths
        """
        return cls.generate_from_directory(force=force)


def main():
    """Generate all VRL configurations from transform directory."""
    OsirVrl.generate_all(force=False)
    print("\nAll VRL configurations generated successfully!")


if __name__ == "__main__":
    main()
