from typing import Union, List, Tuple
import uuid
from osir_lib.core.FileManager import FileManager
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

class SnapshotManager:
    def __init__(self, db_osir):
        self.db = db_osir
