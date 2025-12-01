from typing import Literal

INPUT_TYPE = Literal["file", "dir"]
OS_TYPE = Literal["windows", "linux", "ios", "macos", "network", "android" , "generic"]
MODULE_TYPE = Literal['pre-process','process','post-process']
PROCESSOR_OS = Literal["windows", "unix"]
PROCESSOR_TYPE = Literal["internal", "external"]