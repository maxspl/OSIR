from typing import Optional
from pydantic import BaseModel

from osir_lib.core.model.connector.Json2ElasticModel import Json2ElasticModel
from osir_lib.core.model.connector.Json2SplunkModel import Json2SplunkConfigModel

class OsirConnectorModel(BaseModel):
    splunk: Optional[list[Json2SplunkConfigModel]]
    elastic: Optional[list[Json2ElasticModel]]