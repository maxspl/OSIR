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

NUXT_DIR="/OSIR/OSIR/src/osir_web/"

if [ -d "$NUXT_DIR" ]; then
    echo "[entrypoint] Installing Nuxt dependencies..."
    cd "$NUXT_DIR"

    if [ ! -d "node_modules" ]; then
        npm install --prefer-offline
    fi

    echo "[entrypoint] Building Nuxt app..."
    npm run build

    echo "[entrypoint] Starting Nuxt server (background)..."
    node .output/server/index.mjs &
    NUXT_PID=$!
    echo "[entrypoint] Nuxt PID: $NUXT_PID"
else
    echo "[entrypoint] WARNING: $NUXT_DIR not found, skipping Nuxt."
fi

# Execute the CMD
exec "$@"
