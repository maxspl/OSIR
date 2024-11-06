#!/usr/bin/env bash

ERROR=$(tput setaf 1; echo -n "  [!]"; tput sgr0)
GOODTOGO=$(tput setaf 2; echo -n "  [✓]"; tput sgr0)
INFO=$(tput setaf 3; echo -n "  [-]"; tput sgr0)
MASTER_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
DOCKER_COMPOSE_REPO=$MASTER_DIR/../$1
#export RDP_ADDRESS=$(vagrant rdp | grep -oP '(?<=Address: )\S+(?=:)')
start_docker=true

is_wsl() {
  # Vérifie si /proc/version contient "Microsoft"
  grep -qEi "(microsoft|wsl)" /proc/version &> /dev/null
  return $?
}

start_docker_compose(){
    echo "HOST_HOSTNAME=$(hostname)" > $DOCKER_COMPOSE_REPO/.env
    echo "HOST_IP_LIST=$(hostname -I | tr ' ' ',')" >> $DOCKER_COMPOSE_REPO/.env
    echo "WINDOWS_CORES=$WINDOWS_CORES" >> $DOCKER_COMPOSE_REPO/.env
    # Check if running on WSL
    if is_wsl; then
        echo "WSL_INTEROP=$WSL_INTEROP" >> $DOCKER_COMPOSE_REPO/.env
        echo "OSIR_PATH=$(wslpath -w '$MASTER_DIR/../../../')" >> "$DOCKER_COMPOSE_REPO/.env"    
    fi

    # Check if the DOCKER_PROFILE environment variable is set and not empty
    if [ ! -z "$COMPOSE_PROFILES" ]; then
        # sudo docker compose -f $DOCKER_COMPOSE_REPO/docker-compose.yml --profile $DOCKER_PROFILE up -d
        sudo COMPOSE_PROFILES=$COMPOSE_PROFILES docker compose -f $DOCKER_COMPOSE_REPO/docker-compose.yml up -d
    else 
        sudo docker compose -f $DOCKER_COMPOSE_REPO/docker-compose.yml up -d
    fi
    start_docker=false # Do not start docker compose again
    check_container
}

check_container(){
    # Check for missing docker images in AGENT_DOCKER_IMAGES
    local missing_images=()
    for docker_name in $DOCKER_CONTAINERS; do        
        if ! docker ps | grep "$docker_name" > /dev/null; then
            missing_images+=("$docker_name")
        fi
    done

    if [ ${#missing_images[@]} -gt 0 ]; then
        echo >&2 "${INFO} The following Docker image(s) are not running: ${missing_images[*]}"
        if $start_docker; then
            echo >&2 "${INFO} Let's create them."
            start_docker_compose
        else
            echo >&2 "${ERROR} Failed to run one or more Docker images."
            exit 1
        fi
    else
        echo >&2 "${GOODTOGO} All required Docker images are running."
    fi
}


main(){
    # Check if docker containers are running
    check_container
}

main
