import json
import os
from pathlib import Path, PureWindowsPath
from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()

import io
import logging
from contextlib import contextmanager

@contextmanager
def capture_log_output(target_logger):
    """
    Capture temporairement les logs envoyés à un logger spécifique.
    """
    log_capture_string = io.StringIO()
    temp_handler = logging.StreamHandler(log_capture_string)
    db_fmt = logging.Formatter('[%(levelname)s][%(asctime)s] - %(filename)s:%(lineno)d - %(funcName)s - %(message)s')
    temp_handler.setFormatter(db_fmt)
    target_logger.addHandler(temp_handler)
    try:
        yield log_capture_string
    finally:
        target_logger.removeHandler(temp_handler)

def normalize_osir_path(input_path: str) -> str:
    """
    Ensures the path is relative to the standard /OSIR/share mount point.
    Useful for cleaning absolute paths that include local environment prefixes.
    """
    anchor = "/OSIR/share"
    
    if anchor in str(input_path):
        s_path = str(input_path)
        return s_path[s_path.find(anchor):]
    
    return input_path

def get_latest_log_by_task_id(target_task_id: str, file_path: str = "/OSIR/share/log/task_traces.jsonl"):
    if not os.path.exists(file_path):
        return None

    with open(file_path, 'rb') as f:
        try:
            # On se place à la toute fin du fichier
            f.seek(0, os.SEEK_END)
            pointer = f.tell()
            buffer = bytearray()
            
            while pointer > 0:
                pointer -= 1
                f.seek(pointer)
                char = f.read(1)
                
                # Si on trouve un saut de ligne ou qu'on est au début du fichier
                if char == b'\n' and buffer:
                    # On décode et on vérifie le JSON
                    line = buffer[::-1].decode('utf-8')
                    trace = json.loads(line)
                    if trace.get("task_id") == target_task_id:
                        return trace # On a trouvé le plus récent, on s'arrête
                    buffer = bytearray()
                elif char != b'\n':
                    buffer.extend(char)
            
            # Vérification de la première ligne du fichier (car pas de \n avant)
            if buffer:
                line = buffer[::-1].decode('utf-8')
                trace = json.loads(line)
                if trace.get("task_id") == target_task_id:
                    return trace
                    
        except Exception as e:
            print(f"Erreur de lecture inversée : {e}")
            
    return None