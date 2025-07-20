#!/usr/bin/env bash

ERROR=$(tput setaf 1; echo -n "  [!]"; tput sgr0)
GOODTOGO=$(tput setaf 2; echo -n "  [✓]"; tput sgr0)
INFO=$(tput setaf 3; echo -n "  [-]"; tput sgr0)
DEBUG=$(tput setaf 5; echo -n "  [-]"; tput sgr0)
MASTER_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
DOCKER_COMPOSE_REPO=$MASTER_DIR/../$1

check_winrm(){
    # Run a simple whoami command to winrm is working
    output=$(sudo docker exec agent-agent sh -c \
        "cd /OSIR/setup/setup_scripts; \
        python -c 'import remote_box_setup; \
        remote_box_setup.check_winrm(\"$WIN_DOCKER_HOST\", \"$WIN_DOCKER_USER\", \"$WIN_DOCKER_PASSWORD\", \"$WIN_DOCKER_MOUNT_POINT\", port=55985)'")
    if echo "$output" | grep -q "Successful winrm command"; then
        (echo >&2 "${GOODTOGO} WinRM is working.")
        (echo "${DEBUG} $output") # Print to sdtout for debug only
    else 
        (echo >&2 "${ERROR} WinRM is not working.")
        (echo "${DEBUG} $output") # Print to sdtout for debug only
    fi

    # Check if OSIR already installed. Test-Path returns true is installation path exists
    if echo "$output" | grep -q "True" ; then
        (echo >&2 "${GOODTOGO} OSIR has already been configured on the remote host.")
        (echo "${INFO} $output") # Print to sdtout for debug only
    elif echo "$output" | grep -q "False" ; then
        (echo >&2 "${INFO} OSIR is not configured on the remote host.")
        (echo "${INFO} $output") # Print to sdtout for debug only
        return 1
    else
        (echo >&2 "${INFO} WinRM command for OSIR installation check seems to fails.")
        (echo "${INFO} $output") # Print to sdtout for debug only
        exit 0
    fi
}

configure_OSIR(){
    # Run a simple whoami command to winrm is working
    output=$(sudo docker exec agent-agent sh -c \
        "cd /OSIR/setup/setup_scripts; \
        python -c 'import remote_box_setup; \
        remote_box_setup.setup_OSIR(\"$WIN_DOCKER_HOST\", \"$WIN_DOCKER_USER\", \"$WIN_DOCKER_PASSWORD\", \"/OSIR/setup/windows_setup/src/ps1/setup_OSIR.ps1\", \"$MASTER_IP\", \"$WIN_DOCKER_MOUNT_POINT\")'")
    if echo "$output" | grep -q "Failed winrm"; then
        (echo >&2 "${ERROR} Failed to configure windows box.")
        (echo "${DEBUG} $output") # Print to sdtout for debug only
    else 
        (echo >&2 "${GOODTOGO} Windows box has been configured.")
        (echo "${DEBUG} $output") # Print to sdtout for debug only
    fi
}

check_docker_container_agent_windows() {
  container_name="agent-windows"

  # Check if the container exists
  container_exists=$(powershell.exe -c 'docker ps -a --filter "name=${container_name}" --format "{{.Names}}"' | grep -w "${container_name}")

  if [ -z "$container_exists" ]; then
      (echo >&2 "${INFO} Docker container '${container_name}' does not exist.")
      return 1
  else
      (echo >&2 "${GOODTOGO} Docker container '${container_name}' exists.")
  fi

  # Check if the container is running
  container_running=$(powershell.exe -c 'docker ps --filter "name=${container_name}" --filter "status=running" --format "{{.Names}}"' | grep -w "${container_name}")

  if [ -z "$container_running" ]; then
      (echo >&2 "${ERROR} Docker container '${container_name}' exists but is not running.")
      return 1
  else
      (echo >&2 "${GOODTOGO} Docker container '${container_name}' is running.")
  fi
}

start_docker_desktop() {
    docker_compose_unix_path="$DOCKER_COMPOSE_REPO/docker-compose.yml"
    docker_compose_win_path="$(wslpath -w $docker_compose_unix_path)"

    # Call the function to check if the container exists and is running
    check_docker_container_agent_windows

    # Check if the previous function call was successful
    if [ $? -ne 0 ]; then
            (echo >&2 "${INFO} Docker container 'agent-windows' is not running. Attempting to create and start it using docker-compose...")

            script="
            docker compose -f $docker_compose_win_path up -d
            "
            output=$(powershell.exe -Command "$script")

            # Check if the container was successfully created and started
            check_docker_container_agent_windows

            if [ $? -eq 0 ]; then
                (echo >&2 "${GOODTOGO} Docker container 'agent-windows' was successfully created and started.")
            else
                (echo >&2 "${ERROR} Failed to create and start the Docker container 'agent-windows'.")
                return 1
            fi
    else
            (echo >&2 "${GOODTOGO} Docker container 'agent-windows' is already running. No action needed.")
    fi
}

main() {
    # Save current path
    saved_path=$PWD 
    # cd $MASTER_DIR/../windows_setup/
    # Add ps1 to path
    WINDOWS_POWERSHELL_PATH="/mnt/c/Windows/System32/WindowsPowerShell/v1.0"
    if ! echo $PATH | grep -q "$WINDOWS_POWERSHELL_PATH"; then
        export PATH="$PATH:$WINDOWS_POWERSHELL_PATH"
    fi
    start_docker_desktop
    check_winrm
}

# Input args from agent_setup.sh

main
exit 0
