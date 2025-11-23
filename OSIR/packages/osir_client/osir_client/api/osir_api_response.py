
import json
from osirlib.logger import AppLogger

logger = AppLogger(__name__).get_logger()


class OSIRAPIResponse(object):
    def __init__(self, response: str = None):
        try:
            self._response = json.loads(response)
            
        except Exception as e:
            logger.error_handler(e)