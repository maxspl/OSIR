from typing import Literal

INPUT_TYPE = Literal["file", "dir"]
OS_TYPE = Literal["windows", "unix", "ios", "macos", "network", "android", "generic"]
MODULE_TYPE = Literal['pre-process', 'process', 'post-process', 'post_parsing']
PROCESSOR_OS = Literal["windows", "unix"]
PROCESSOR_TYPE = Literal["internal", "external"]
OUTPUT_TYPE = Literal["single_file", "None", "multiple_files"]