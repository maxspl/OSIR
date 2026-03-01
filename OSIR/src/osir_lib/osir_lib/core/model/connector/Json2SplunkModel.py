from typing import Optional
from pydantic import BaseModel


class Json2SplunkConfigModel(BaseModel):
    """
        Configuration model for the Json2Splunk data ingestion engine.

        Attributes:
            source (str): The logical source name for the data in Splunk.
            sourcetype (str): The Splunk sourcetype used for field extraction and CIM mapping.
            name_rex (str): Regular expression used to extract the artifact name from the file path.
            path_suffix (str): File extension or suffix to filter for (e.g., '.json' or '.jsonl').
            host_rex (str): Regular expression used to identify the host/endpoint from the path metadata.
            timestamp_path (Optional[list[str]]): A list representing the key path to the primary 
                timestamp field in the JSON (e.g., ["Metadata", "CreatedTime"]).
            timestamp_format (str): The strftime-compatible format used to parse the timestamp_path.
            artifact (str): The category or type of forensic artifact (e.g., 'prefetch', 'mft').
    """
    source: str
    sourcetype: str
    name_rex: str
    path_suffix: Optional[str] = None
    host_rex: str
    timestamp_path: Optional[list[str]]
    timestamp_format: str
    artifact: Optional[str] = None
