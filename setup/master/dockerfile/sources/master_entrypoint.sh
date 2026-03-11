#!/bin/bash

# install quietly and only report on failure
safe_install() {
    if ! pip install --no-build-isolation -e "$1" --break-system-packages --ignore-installed > /dev/null 2>&1; then
        echo "ERROR: Failed to install $1"
        exit 1
    fi
}

# Run the installations
safe_install "/OSIR/OSIR/src/osir_service/"
safe_install "/OSIR/OSIR/src/osir_lib/"
safe_install "/OSIR/OSIR/src/osir_web/"

# Execute the CMD
exec "$@"
