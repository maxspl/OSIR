save_images(){   
    local TYPE="$1"
    TARGET_DIR="$CURRENT_DIR/../offline_release"
    case "$TYPE" in
        master)
            TARGET_FILE="$TARGET_DIR/master_containers.tar"
            ;;
        agent)
            TARGET_FILE="$TARGET_DIR/agent_containers.tar"
            ;;
        win)
            TARGET_FILE="$TARGET_DIR/win_containers.tar"
            ;;
        splunk)
            TARGET_FILE="$TARGET_DIR/splunk_containers.tar"
            ;;
        *)
            echo "${ERROR} Invalid type: $TYPE"
            exit 1
            ;;
    esac

    # Ensure the target directory exists
    mkdir -p "$TARGET_DIR"

    # Convert the IMAGES environment variable into an array
    read -r -a IMAGES <<< "$IMAGES"

    # Initialize arrays
    SAVED_IMAGES=()
    MISSING_IMAGES=()

    echo "${INFO} IMAGES: ${IMAGES[*]}"

    # Check which images exist
    for IMAGE in "${IMAGES[@]}"; do
        echo "${INFO} Checking IMAGE: $IMAGE"
        if docker image inspect "$IMAGE" > /dev/null 2>&1; then
            SAVED_IMAGES+=("$IMAGE")
        else
            MISSING_IMAGES+=("$IMAGE")
        fi
    done

    # Handle missing images
    if [ ${#MISSING_IMAGES[@]} -gt 0 ]; then
        echo "${ERROR} Skipping non-existent images: ${MISSING_IMAGES[*]}"
    fi

    # Save images if available
    if [ ${#SAVED_IMAGES[@]} -gt 0 ]; then
        echo "${GOODTOGO} Saving the following images: ${SAVED_IMAGES[*]}"
        docker save -o "$TARGET_FILE" "${SAVED_IMAGES[@]}"
        if [ $? -eq 0 ]; then
            ABSOLUTE_TARGET_FILE=$(realpath "$TARGET_FILE")
            echo "${GOODTOGO} Images saved successfully to: $ABSOLUTE_TARGET_FILE"
        else
            echo "${ERROR} Failed to save images."
        fi
    else
        echo "${ERROR} No valid images to save."
    fi
}

main(){
    # Determine the directory where the script resides
    CURRENT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

    case "$type" in
        master|agent|win|splunk)
            echo "${INFO} Running as $type."
            save_images "$type"
            ;;
        *)
            echo "${ERROR} Invalid type: $type"
            exit 1
            ;;
    esac
}

# Define status messages with colors
ERROR=$(tput setaf 1; echo -n "  [!]"; tput sgr0)
GOODTOGO=$(tput setaf 2; echo -n "  [✓]"; tput sgr0)
INFO=$(tput setaf 3; echo -n "  [-]"; tput sgr0)

type=$1 # master, agent, win, splunk

main
