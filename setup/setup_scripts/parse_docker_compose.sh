#!/bin/bash

parse_docker_compose(){

    # yq URL
    YQ_URL="https://github.com/mikefarah/yq/releases/download/v4.44.2/yq_linux_amd64"
    YQ_BINARY="$CURRENT_DIR/yq"

    # Ensure yq is available
    if [[ ! -f "$YQ_BINARY" ]]; then
        echo "yq not found in $CURRENT_DIR. Downloading yq..."
        wget -O "$YQ_BINARY" "$YQ_URL"
        chmod +x "$YQ_BINARY"
    fi

    # Ensure yq is executable
    if [[ ! -x "$YQ_BINARY" ]]; then
        echo "yq is not executable. Please check the permissions."
        exit 1
    fi

    # Path to your docker-compose file
    COMPOSE_FILE="$DOCKER_COMPOSE_REPO/docker-compose.yml"

    # Check if the docker-compose file exists
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        echo "File $COMPOSE_FILE does not exist."
        exit 1
    fi

    if [[ ${#PROFILES[@]} -eq 0 ]]; then
        # No profiles specified, return all containers
        CONTAINERS=$("$YQ_BINARY" e '.services[].container_name' "$COMPOSE_FILE" | tr "\n" " ")
    else
        # Create a yq expression to match any of the specified profiles
        YQ_EXPRESSION=""
        for profile in "${PROFILES[@]}"; do
            YQ_EXPRESSION+='.value.profiles[] == "'"$profile"'" or '
        done
        YQ_EXPRESSION=${YQ_EXPRESSION% or }  # Remove trailing " or "

        # Parse the docker-compose file and extract the containers with matching profiles
        CONTAINERS=$("$YQ_BINARY" e ".services | with_entries(select(.value.profiles and ($YQ_EXPRESSION))) | .[] | .container_name" "$COMPOSE_FILE" | tr "\n" " ")

        # If no containers found with profiles, check for containers without profiles (unprofiled services)
        if [[ -z "$CONTAINERS" ]]; then
            CONTAINERS=$("$YQ_BINARY" e ".services | with_entries(select(.value.profiles == null or .value.profiles == [])) | .[] | .container_name" "$COMPOSE_FILE" | tr "\n" " ")
        fi
    fi

    # Print the containers if any are found
    if [[ -n "$CONTAINERS" ]]; then
        echo "$CONTAINERS"
    else
        echo "No containers found for profiles '${PROFILES[*]}' or in unprofiled services."
    fi
}

main(){
    # Determine the directory where the script resides
    CURRENT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
    if [ "$type" = "agent" ] ; then  
        # Agent docker-compose
        DOCKER_COMPOSE_REPO=$CURRENT_DIR/../agent
    elif [ "$type" = "master" ] ; then  
        # Master docker-compose
        DOCKER_COMPOSE_REPO=$CURRENT_DIR/../master
    elif [ "$type" = "standalone" ] ; then  
        # Standalone docker-compose
        DOCKER_COMPOSE_REPO=$CURRENT_DIR/../standalone
    fi

    # Convert COMPOSE_PROFILES environment variable into an array of profiles
    if [[ -n "$COMPOSE_PROFILES" ]]; then
        IFS=',' read -r -a PROFILES <<< "$COMPOSE_PROFILES"
    else
        PROFILES=() # Empty array if no profiles are set
    fi

    # Run the parse_docker_compose function
    parse_docker_compose
}

type=$1 # master, agent, or standalone

main
