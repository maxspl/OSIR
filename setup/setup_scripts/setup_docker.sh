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

start_docker_compose() {
    ENV_FILE="$DOCKER_COMPOSE_REPO/.env"

    # Ensure .env exists and ends with a newline
    touch "$ENV_FILE"
    [ -s "$ENV_FILE" ] && tail -c1 "$ENV_FILE" | read -r _ || echo >> "$ENV_FILE"

    # Helper to update or append variable
    set_env_var() {
        local var_name="$1"
        local var_value="$2"

        if grep -q "^$var_name=" "$ENV_FILE"; then
            sed -i "s|^$var_name=.*|$var_name=$var_value|" "$ENV_FILE"
        else
            echo "$var_name=$var_value" >> "$ENV_FILE"
        fi
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
    # Check if docker containers are running
    check_container
}

main
