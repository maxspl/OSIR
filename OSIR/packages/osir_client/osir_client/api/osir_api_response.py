
import json
from osirlib.logger import AppLogger

logger = AppLogger(__name__).get_logger()


class OSIRAPIResponse(object):
    def __init__(self, response: dict = None):
        try:
            self.version = response.get('version', None)
            self.status = response.get('status', None)
            self.response = response.get('response')

        except Exception as e:
            logger.error_handler(e)