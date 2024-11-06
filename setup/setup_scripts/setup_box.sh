#!/usr/bin/env bash

ERROR=$(tput setaf 1; echo -n "  [!]"; tput sgr0)
GOODTOGO=$(tput setaf 2; echo -n "  [✓]"; tput sgr0)
INFO=$(tput setaf 3; echo -n "  [-]"; tput sgr0)
DEBUG=$(tput setaf 5; echo -n "  [-]"; tput sgr0)
MASTER_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

start_box(){
    vagrant up
}

# check_winrm(){
#     # Run a simple whoami command to winrm is working
#     output=$(sudo docker exec agent-agent sh -c \
#         "cd /OSIR/setup/setup_scripts; \
#         python3.11 -c 'import remote_box_setup; \
#         remote_box_setup.check_winrm(\"$host\", \"$user\", \"$password\", \"$mount_point\")'")
#     if echo "$output" | grep -q "Successful winrm command"; then
#         (echo >&2 "${GOODTOGO} WinRM is working.")
#         (echo "${DEBUG} $output") # Print to sdtout for debug only
#     else 
#         (echo >&2 "${ERROR} WinRM is not working.")
#         (echo "${DEBUG} $output") # Print to sdtout for debug only
#     fi

#     # Check if OSIR already installed. Test-Path returns true is installation path exists
#     if echo "$output" | grep -q "True" ; then
#         (echo >&2 "${GOODTOGO} OSIR has already been configured on the remote host.")
#         (echo "${INFO} $output") # Print to sdtout for debug only
#     elif echo "$output" | grep -q "False" ; then
#         (echo >&2 "${INFO} OSIR is not configured on the remote host.")
#         (echo "${INFO} $output") # Print to sdtout for debug only
#         return 1
#     else
#         (echo >&2 "${INFO} WinRM command for OSIR installation check seems to fails.")
#         (echo "${INFO} $output") # Print to sdtout for debug only
#         exit 0
#     fi
# }

check_winrm(){
    # Run a simple whoami command to check if WinRM is working
    output=$(sudo docker exec agent-agent sh -c \
        "cd /OSIR/setup/setup_scripts; \
        python3.11 -c 'import remote_box_setup; \
        remote_box_setup.check_winrm(\"$host\", \"$user\", \"$password\", \"$mount_point\")'")
    
    if echo "$output" | grep -q "Successful winrm command"; then
        (echo >&2 "${GOODTOGO} WinRM is working.")
        (echo "${DEBUG} $output") # Print to stdout for debug only
        return 0
    else 
        (echo >&2 "${ERROR} WinRM is not working.")
        (echo "${DEBUG} $output") # Print to stdout for debug only
        return 1
    fi
}

is_OSIR_installed(){
    output=$(sudo docker exec agent-agent sh -c \
        "cd /OSIR/setup/setup_scripts; \
        python3.11 -c 'import remote_box_setup; \
        remote_box_setup.check_winrm(\"$host\", \"$user\", \"$password\", \"$mount_point\")'")
    # Check if OSIR is already installed. Test-Path returns true if installation path exists
    if echo "$output" | grep -q "True"; then
        (echo >&2 "${GOODTOGO} OSIR has already been configured on the remote host.")
        (echo "${INFO} $output") # Print to stdout for debug only
        return 0
    elif echo "$output" | grep -q "False"; then
        (echo >&2 "${INFO} OSIR is not configured on the remote host.")
        (echo "${INFO} $output") # Print to stdout for debug only
        return 1
    else
        (echo >&2 "${INFO} WinRM command for OSIR installation check seems to have failed.")
        (echo "${INFO} $output") # Print to stdout for debug only
        return 1
    fi
}

check_smb(){
    # Check if smb share can be accessed from windows
    output=$(sudo docker exec agent-agent sh -c \
        "cd /OSIR/setup/setup_scripts; \
        python3.11 -c 'import remote_box_setup; \
        remote_box_setup.check_smb(\"$host\", \"$user\", \"$password\", \"/OSIR/setup/windows_setup/src/ps1/setup_unsecure_smb.ps1\", \"$MASTER_IP\")'") #$MASTER_IP from env
    if echo "$output" | grep -q "Failed winrm"; then 
        (echo >&2 "${ERROR} SMB share cannot be accessed from Windows box.")
        (echo "${DEBUG} $output") # Print to sdtout for debug only
    else 
        (echo >&2 "${GOODTOGO} SMB share can be accessed from Windows box..")
        (echo "${DEBUG} $output") # Print to sdtout for debug only
    fi
}
check_box_running(){
    # Check if the VM named "dfir" is up
    vagrant_status=$(vagrant status | grep dfir_box)
    if vagrant status | grep -q "dfir_box" && ! vagrant status | grep -E -q "dfir_box\s+not created"; then
        # Check if the VM is running
        if vagrant status | grep -q "running"; then
            (echo >&2 "${GOODTOGO} The box is running.")
        else
            (echo >&2 "${INFO} The box exists but is not running.")
            (echo >&2 "${INFO} Lets start it.")
            start_box
            check_box_running
        fi
    elif vagrant status | grep -qP "dfir_box\s+not created" ; then
        (echo >&2 "${INFO} The box does not exist.")
        (echo >&2 "${INFO} Lets make it...")
        start_box
        check_box_running
    else
        (echo >&2 "${INFO} The box does not exist.")
        (echo >&2 "${INFO} Lets make it...")
        start_box
        check_box_running
    fi
}

configure_OSIR(){
    # Run a simple whoami command to winrm is working
    output=$(sudo docker exec agent-agent sh -c \
        "cd /OSIR/setup/setup_scripts; \
        python3.11 -c 'import remote_box_setup; \
        remote_box_setup.setup_OSIR(\"$host\", \"$user\", \"$password\", \"/OSIR/setup/windows_setup/src/ps1/setup_OSIR.ps1\", \"$MASTER_IP\", \"$mount_point\")'")
    if echo "$output" | grep -q "Failed winrm"; then
        (echo >&2 "${ERROR} Failed to configure windows box.")
        (echo "${DEBUG} $output") # Print to sdtout for debug only
    else 
        (echo >&2 "${GOODTOGO} Windows box has been configured.")
        (echo "${DEBUG} $output") # Print to sdtout for debug only
    fi
}

main() {
    # Save current path
    saved_path=$PWD 
    if [ "$host" = "host.docker.internal" ] ; then # change for dev if remote is actually local to avoid starting local box
        # Enter the vagrant directory 
        cd $MASTER_DIR/../windows_setup/
        check_box_running
        cd $saved_path
    fi

    # if ! check_winrm; then # Enter if winrm is OSIR is not already installed
    #     check_smb
    #     configure_OSIR
    # fi

    # Capture both the output and the exit status of the check_winrm function
    output=$(check_winrm)    # Capture output
    winrm_status=$?          # Capture exit status
    # If DEBUG_MODE is set, print the check_winrm output
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "$output"
    fi
    
    if [ -n "$winrm_status" ] && [ "$winrm_status" -ne 0 ]; then
        if [[ -n "$DOCKUR_SETUP" ]]; then
            (echo >&2 "${INFO} Waiting for WinRM to be available. Normal behavior if first setup of Windows in docker...")
            (echo >&2 "${INFO} You can follow Windows setup here : http://$host:8006")
            start_time=$(date +%s)
            timeout=600 # 10 minutes in seconds

            while true; do
                # Capture both the output and the exit status in the loop
                output=$(check_winrm >/dev/null 2>&1)
                winrm_status=$?  # Capture the exit status again

                # If DEBUG_MODE is set, print the check_winrm output
                if [ "$DEBUG_MODE" = "true" ]; then
                    echo "$output"
                fi

                if [ "$winrm_status" -eq 0 ]; then
                    break  # Exit the loop if check_winrm is successful
                fi

                current_time=$(date +%s)
                elapsed_time=$((current_time - start_time))

                if [[ $elapsed_time -ge $timeout ]]; then
                    (echo >&2 "${ERROR} WinRM is still not working after 10 minutes. Stopping. Check dockur logs and go check http://$host:8006.")
                    exit 1
                fi

                sleep 30 # Retry every 30 seconds
            done
        fi
    fi

    # Check if OSIR is installed, only run configure_OSIR if it's not installed
    if ! is_OSIR_installed; then
        configure_OSIR
    fi

    check_smb
}

# Input args from agent_setup.sh
host=$1
user=$2
password=$3
mount_point=$4
main $host $user $password $mount_point
exit 0