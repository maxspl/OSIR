#!/usr/bin/env bash

ERROR=$(tput setaf 1; echo -n "  [!]"; tput sgr0)
GOODTOGO=$(tput setaf 2; echo -n "  [✓]"; tput sgr0)
INFO=$(tput setaf 3; echo -n "  [-]"; tput sgr0)
MASTER_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
DOCKER_COMPOSE_REPO=$MASTER_DIR/../$1
#export RDP_ADDRESS=$(vagrant rdp | grep -oP '(?<=Address: )\S+(?=:)')
start_docker=true

is_wsl() {
  # Check if /proc/version contains "Microsoft"
  grep -qEi "(microsoft|wsl)" /proc/version &> /dev/null
  return $?
}

is_systemd() {
  # Check if PID 1 is systemd (WSL with systemd=true)
  [ "$(ps -p 1 -o comm=)" = "systemd" ]
}

is_root_shared() {
  # 'rshared' bind mounts from the docker-compose files require / to be a shared mount
  findmnt -no PROPAGATION / 2> /dev/null | grep -q shared
}

check_wsl_docker(){
    # On WSL, / is not a shared mount by default and starting containers
    # fails with "it is not a shared mount"
    if ! is_wsl; then
        return 0
    fi

    # Without systemd, nothing starts the daemon on WSL boot: start it if needed
    if ! is_systemd && ! docker info > /dev/null 2>&1; then
        (echo >&2 "${INFO} Docker daemon is not running, starting it.")
        sudo service docker start
    fi

    if is_root_shared; then
        return 0
    fi

    if is_systemd; then
        # With systemd=true, WSL keeps separate mount namespaces for sessions
        # and services: a make-shared started here never reaches the Docker
        # daemon's namespace. Only a WSL reconfiguration can fix it.
        (echo >&2 "${ERROR} WSL runs with systemd enabled: the Docker daemon lives in a separate mount namespace.")
        (echo >&2 "${ERROR} 'rshared' bind mounts cannot work in this state.")
        (echo >&2 "${INFO} Update /etc/wsl.conf with:")
        (echo >&2 "${INFO}   [boot]")
        (echo >&2 "${INFO}   systemd=false")
        (echo >&2 "${INFO}   command = mount --make-shared / && service docker start")
        (echo >&2 "${INFO} Then from Windows run 'wsl --shutdown' and reopen WSL.")
        exit 1
    fi

    (echo >&2 "${INFO} Making / a shared mount for 'rshared' bind mounts.")
    sudo mount --make-shared /
    if ! is_root_shared; then
        (echo >&2 "${ERROR} Failed to make / a shared mount.")
        exit 1
    fi
    (echo >&2 "${INFO} Note: this change is lost at each WSL restart. To make it persistent, add to /etc/wsl.conf:")
    (echo >&2 "${INFO}   [boot]")
    (echo >&2 "${INFO}   command = mount --make-shared / && service docker start")
}

start_docker_compose() {
    ENV_FILE="$DOCKER_COMPOSE_REPO/.env"

    # Ensure .env exists and ends with a newline
    touch "$ENV_FILE"
    [ -s "$ENV_FILE" ] && tail -c1 "$ENV_FILE" | read -r _ || echo >> "$ENV_FILE"

    # Helper to update or append variable
    set_env_var() {
        local var_name="$1"
        local var_value="$2"

        sed -i "/^$var_name=/d" "$ENV_FILE"
        echo "$var_name=$var_value" >> "$ENV_FILE"
    }

    set_env_var "HOST_HOSTNAME" "$(hostname)"
    set_env_var "HOST_IP_LIST" "$(hostname -I | tr ' ' ',')"
    set_env_var "WINDOWS_CORES" "$WINDOWS_CORES"

    if is_wsl; then
        set_env_var "WSL_INTEROP" "$WSL_INTEROP"
        set_env_var "OSIR_PATH" "$(wslpath -w "$MASTER_DIR/../../../")"
    fi

    if [ -n "$COMPOSE_PROFILES" ]; then
        sudo COMPOSE_PROFILES="$COMPOSE_PROFILES" docker compose -f "$DOCKER_COMPOSE_REPO/docker-compose.yml" up -d
    else 
        sudo docker compose -f "$DOCKER_COMPOSE_REPO/docker-compose.yml" up -d
    fi

    start_docker=false
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
    # Check WSL specifics (docker daemon, shared mount for 'rshared' binds)
    check_wsl_docker
    # Check if docker containers are running
    check_container
}

main
