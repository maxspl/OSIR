from enum import Enum


class ProcessingStatus(str, Enum):
    TASK_CREATED = "task_created"
    PROCESSING_STARTED = "processing_started"
    PROCESSING_DONE = "processing_done"
    PROCESSING_FAILED = "processing_failed"
