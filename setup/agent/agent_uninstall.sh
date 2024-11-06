#!/usr/bin/env bash

ERROR=$(tput setaf 1; echo -n "  [!]"; tput sgr0)
GOODTOGO=$(tput setaf 2; echo -n "  [✓]"; tput sgr0)
INFO=$(tput setaf 3; echo -n "  [-]"; tput sgr0)
USERINPUT=$(tput setaf 4; echo -n "  [?]"; tput sgr0)
MASTER_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
DOCKER_COMPOSE_REPO="$MASTER_DIR/../agent"
VAGRANT_PROJECT_DIR="$MASTER_DIR/../windows_setup"
VAGRANT_DIR="$VAGRANT_PROJECT_DIR/.vagrant"
DOCKUR_DIR="$MASTER_DIR/../windows_setup/src/dockur_storage"

# Parse command line arguments
while getopts "hvdi" arg; do
  case $arg in
    h)
      show_help=true
      ;;
    v)
      vagrant_delete=true
      ;;
    d)
      dockur_delete=true
      ;;
    i)
      images_delete=true
      ;;
    *)
      echo "Unknown argument: -$OPTARG"
      exit 1
      ;;
  esac
done

main() {
    # Check if the script is run as root
    if [ "$EUID" -ne 0 ]; then
        (echo >&2 "${ERROR} This script must be run as root.")
        exit 1
    fi

    if [ "$show_help" = true ]; then
        echo "Usage: $0 [-v] [-d] [-i] [-h]"
        echo "Options:"
        echo "  -v  Delete Vagrant VM"
        echo "  -d  Delete Dockur VM"
        echo "  -i  Remove all Docker images"
        echo "  -h  Show help"
        exit 0
    fi

    # Change to the Docker Compose repository directory
    cd "$DOCKER_COMPOSE_REPO" || exit 1

    if [ "$images_delete" = true ]; then
        echo "${INFO} Removing all Docker images..."
        docker compose --profile all down --rmi all --volumes --remove-orphans
    else
        echo "${INFO} Bringing down Docker containers..."
        docker compose --profile all down --volumes --remove-orphans
    fi

    if [ "$vagrant_delete" = true ]; then
        echo "${INFO} Destroying Vagrant VM..."
        cd "$VAGRANT_PROJECT_DIR" || exit 1
        vagrant destroy -f
        echo "${INFO} Removing VAGRANT_DIR..."
        rm -rf "$VAGRANT_DIR"
    fi

    if [ "$dockur_delete" = true ]; then
        echo "${INFO} Removing DOCKUR_DIR..."
        rm -rf "$DOCKUR_DIR"
    fi
}

main
exit 0
