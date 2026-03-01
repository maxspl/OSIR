from typing import Optional
from pydantic import BaseModel


class OsirToolModel(BaseModel):
    """
        Data model defining the execution parameters for a tool.

        Attributes:
            path (str): The relative or absolute path to the tool binary 
                within the /OSIR/bin/ environment.
            cmd (str): The command-line template containing placeholders 
                (e.g., {input_file}, {output_dir}) that are resolved at runtime.
            source (str, optional): The origin or download URL of the tool.
            version (str | float, optional): The specific version of the forensic tool.
            license (str, optional): The licensing type (e.g., MIT, GPL, Proprietary).
            env (list[str], optional): A list of environment variables required 
                for the tool's execution (e.g., ["VAR=VALUE"]).
    """
    path: str
    cmd: str
    source: Optional[str] = None
    version: Optional[str | float] = None
    license: Optional[str] = None
    env: Optional[list[str]] = None
