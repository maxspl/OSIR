#!/usr/bin/env bash

ERROR=$(tput setaf 1; echo -n "  [!]"; tput sgr0)
GOODTOGO=$(tput setaf 2; echo -n "  [✓]"; tput sgr0)
INFO=$(tput setaf 3; echo -n "  [-]"; tput sgr0)
DEBUG=$(tput setaf 5; echo -n "  [-]"; tput sgr0)
MASTER_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
WINDOWS_SETUP_REPO=$MASTER_DIR/../$1


configure_OSIR(){
    (echo >&2 "${GOODTOGO} Let's configure OSIR on the Windows Host.")

    # create a file to allow setup_OSIR.ps1 to determine correct paths (on disk instead of smb)
    # this file also contain path of OSIR 
    identifier_file="/mnt/c/Windows/Temp/local_host_identifier.OSIR" # It should print \\wsl.localhost\<VM OS>\<path to OSIR>\OSIR
    touch $identifier_file
    wslpath -w  "$MASTER_DIR/../.." > $identifier_file

    # copy setup ps1 to disk to avoid executing from \\wsl and then get a warning preventing execution
    SETUP_PS1=$WINDOWS_SETUP_REPO/src/ps1/setup_OSIR.ps1
    cp $SETUP_PS1 /mnt/c/Windows/Temp/setup_OSIR.ps1

    # Run the ps1 script on the Windows host
    if $debug_mode; then
        powershell.exe -ExecutionPolicy Bypass -File "C:\Windows\Temp\setup_OSIR.ps1"
    else
        powershell.exe -ExecutionPolicy Bypass -File "C:\Windows\Temp\setup_OSIR.ps1" > /dev/null
    fi
}


main() {
    # Add ps1 to path
    WINDOWS_POWERSHELL_PATH="/mnt/c/Windows/System32/WindowsPowerShell/v1.0"
    if ! echo $PATH | grep -q "$WINDOWS_POWERSHELL_PATH"; then
        export PATH="$PATH:$WINDOWS_POWERSHELL_PATH"
    fi
    # Check if the directory /mnt/c/OSIR does not exist
    if [ ! -d "/mnt/c/OSIR" ]; then
        configure_OSIR
    fi
}

# Input args from agent_setup.sh

main
exit 0