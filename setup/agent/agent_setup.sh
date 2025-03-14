#!/usr/bin/env bash

# 1. Enter interactive (by default) or automated configuration depending on option selected by user
# 2. Get Master host : FQDN or IP
# 3. If Windows box is local : 
#     - check and install requirements (vbox, vagrant, docker)
#     - check if agent docker container is running (start it if not)
# 4. If Windows box is remote :
#     - check and install requirements (docker)
# 5. If master is remote :
#     - check if samba share can be accessed
# 6. If Windows box is local : 
#     - check if box is running
#     - run the box
#     - check if winrm is working
#     - check if Windows box can access Samba share
#     - check if OSIR is already installed, install it via Winrm ps1 scripts if not
# 7. If Windows box is remote : 
#     - check if winrm is working
#     - check if Windows box can access Samba share
#     - check if OSIR is already installed, install it via Winrm ps1 scripts if not
# 8. If installation is manual, save installation parameters to config file agent.yml

# Notes: 
#     - host.docker.internal is used for docker -> vagrant winrm as localhost cannot be requested from docker (winrm listening on the host, not the docker)
#     - 10.0.2.2 is used for vagrant -> host to access smb share

# To do : stop if check is 6/7 didnt work

ERROR=$(tput setaf 1; echo -n "  [!]"; tput sgr0)
GOODTOGO=$(tput setaf 2; echo -n "  [✓]"; tput sgr0)
INFO=$(tput setaf 3; echo -n "  [-]"; tput sgr0)
USERINPUT=$(tput setaf 4; echo -n "  [?]"; tput sgr0)
MASTER_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
SETUP_SCRIPT_PATH=$(realpath "$MASTER_DIR/../setup_scripts")
CONF_PATH=$(realpath "$MASTER_DIR/../conf")

debug_mode=false
config_mode=false # If set, nothing is ask to the user. Configuration is pulled from agent.yml
offline_mode=false 

# Regular expression to match an IP address
ip_regex='^([0-9]{1,3}\.){3}[0-9]{1,3}$'
# Regular expression to match an FQDN
fqdn_regex='^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Parse command line arguments
while getopts "hdco" arg; do
  case $arg in
    h)
      show_help=true
      ;;
    d)
      debug_mode=true
      ;;
    c)
      config_mode=true
      ;;
    o)
      offline_mode=true
      ;;
    *)
      echo "Unknown argument: $arg"
      exit 1
      ;;
  esac
done

export DEBUG_MODE=$debug_mode
export OFFLINE_MODE=$offline_mode

get_yml_value(){
    source $SETUP_SCRIPT_PATH/yaml.sh
    parse_yaml $CONF_PATH/agent.yml | grep $2 | grep -oP '"(.*)"' | tr -d '"'
}

# Check if submited IP or FQDN is localhost
function check_localhost {
    local input="$1"
    # Fetch all IPs associated with the hostname input
    local ip_addresses=$(getent hosts "$input" | awk '{ print $1 }')
    # Fetch all local IPs from the system's network interfaces
    local local_ips=$(hostname -I)

    for ip in $ip_addresses; do
        # Check if the IP is the localhost IP or in the list of local IPs
        if [[ "$ip" == "127.0.0.1" || "$ip" == "::1" || $local_ips =~ $ip ]]; then
            return 0
        fi
    done

    return 1
}

local_installation(){
    # Launch Docker
    # OFFLINE MODE: decide which Docker Compose profile/service to use
    if $offline_mode; then
        # Offline uses the agent-offline service (prebuilt)
        if is_wsl; then
            export COMPOSE_PROFILES="wsl,agent-offline"
        else
            export COMPOSE_PROFILES="agent-offline"
        fi
        export DOCKER_CONTAINERS=$(bash "$SETUP_SCRIPT_PATH/parse_docker_compose.sh" agent)

        if $debug_mode; then
            $SETUP_SCRIPT_PATH/setup_docker.sh agent
        else
            $SETUP_SCRIPT_PATH/setup_docker.sh agent > /dev/null
        fi
    else
        # Normal (online) mode: build from Dockerfile
        if is_wsl; then
            export COMPOSE_PROFILES="wsl"
        else
            export COMPOSE_PROFILES="default"
        fi
        export DOCKER_CONTAINERS=$(bash "$SETUP_SCRIPT_PATH/parse_docker_compose.sh" agent)

        if $debug_mode; then
            $SETUP_SCRIPT_PATH/setup_docker.sh agent
        else
            $SETUP_SCRIPT_PATH/setup_docker.sh agent > /dev/null
        fi
    fi

    if [ $? -eq 1 ]; then
        (echo >&2 "${ERROR} Failed to launch docker requirements.")
        exit 1
    fi
    
    if ! is_wsl; then
        # Export to env requirements
        export RAM_REQ="17000000"
        export DISK_REQ="50000"

        if $debug_mode; then
            $SETUP_SCRIPT_PATH/requirements.sh vbox
        else
            $SETUP_SCRIPT_PATH/requirements.sh vbox > /dev/null
        fi

        host="host.docker.internal"
        user="vagrant"
        password="vagrant"
        mount_point="C:"
        if $debug_mode; then
            $SETUP_SCRIPT_PATH/setup_box.sh $host $user $password $mount_point
        else
            $SETUP_SCRIPT_PATH/setup_box.sh $host $user $password $mount_point > /dev/null
        fi
    else
        (echo >&2 "${INFO} Running in WSL, Vagrant will not be setup.")

        if $debug_mode; then
            $SETUP_SCRIPT_PATH/setup_windows_host.sh windows_setup
        else
            $SETUP_SCRIPT_PATH/setup_windows_host.sh windows_setup > /dev/null
        fi
    fi

    check_localhost $master_host
    if [ $? -eq 0 ]; then
        (echo >&2 "${INFO} Master is localhost, agent will not use Samba.")
    else
        (echo >&2 "${INFO} Master is not localhost, agent will use Samba.")
        if $debug_mode; then
            $SETUP_SCRIPT_PATH/check_samba.sh
        else
            $SETUP_SCRIPT_PATH/check_samba.sh > /dev/null
        fi
    fi
    if [ $? -eq 1 ]; then
        exit 1
    fi
}

is_wsl() {
  # Vérifie si /proc/version contient "Microsoft"
  grep -qEi "(microsoft|wsl)" /proc/version &> /dev/null
  return $?
}

remote_installation(){
    # Export to env requirements
    export RAM_REQ="17000000" # ~16GB of ram
    export DISK_REQ="50000"  # 16GB of disk

    # Check and install requirements
    if $debug_mode; then
        $SETUP_SCRIPT_PATH/requirements.sh 
    else
        $SETUP_SCRIPT_PATH/requirements.sh > /dev/null
    fi

    # OFFLINE MODE in remote installation
    if $offline_mode; then
        export COMPOSE_PROFILES="agent-offline"
        export DOCKER_CONTAINERS=$(bash "$SETUP_SCRIPT_PATH/parse_docker_compose.sh" agent)

        if $debug_mode; then
            $SETUP_SCRIPT_PATH/setup_docker.sh agent
        else
            $SETUP_SCRIPT_PATH/setup_docker.sh agent > /dev/null
        fi
    else
        export COMPOSE_PROFILES="default"
        export DOCKER_CONTAINERS=$(bash "$SETUP_SCRIPT_PATH/parse_docker_compose.sh" agent)

        if $debug_mode; then
            $SETUP_SCRIPT_PATH/setup_docker.sh agent
        else
            $SETUP_SCRIPT_PATH/setup_docker.sh agent > /dev/null
        fi
    fi

    if [ $? -eq 1 ]; then
        (echo >&2 "${ERROR} Failed to launch docker requirements.")
        exit 1
    fi
    # Check if Master is localhost
    check_localhost $master_host
    # Check exit code
    if [ $? -eq 0 ]; then
        (echo >&2 "${INFO} Master is localhost, agent will not use Samba.")
    elif [ $? -eq 1 ]; then
        (echo >&2 "${INFO} Master is not localhost, agent will use Samba.")
        # Check if samba is working
        if $debug_mode; then
            $SETUP_SCRIPT_PATH/check_samba.sh 
        else
            $SETUP_SCRIPT_PATH/check_samba.sh > /dev/null
        fi
    fi
    # Check exit code : stop if Samba share cannot be accessed
    if [ $? -eq 1 ]; then
        exit 1
    fi

    # Setup Windows box
    host=$1
    user=$2
    password=$3
    mount_point=$4
    if $debug_mode; then
        $SETUP_SCRIPT_PATH/setup_box.sh $host $user $password $mount_point
    else
        $SETUP_SCRIPT_PATH/setup_box.sh $host $user $password $mount_point > /dev/null
    fi

}
setup_dockur_win(){
    # Define the directories
    # ISO_URL="https://archive.org/download/tiny-10-23-h2/tiny10%20x64%2023h2.iso" 
    ISO_URL="https://natopia.fr/tiny10_x64_23h2.iso"
    ISO_NAME="tiny10_x64_23h2.iso"
    ISO_DIR="$MASTER_DIR/../windows_setup/src/win_iso"
    DOCKUR_STORAGE_DIR="$MASTER_DIR/../windows_setup/src/dockur_storage"
    CUSTOM_ISO_NAME="custom.iso"

    # Ensure the directories exist
    mkdir -p "$ISO_DIR"
    mkdir -p "$DOCKUR_STORAGE_DIR"

    # Check if the ISO already exists
    if [ ! -f "$ISO_DIR/$ISO_NAME" ]; then
        (echo >&2 "${INFO} ISO not found. Downloading...")
        
        # Download the ISO into the win_iso directory
        wget -O "$ISO_DIR/$ISO_NAME" "$ISO_URL"
        
        # Verify the download was successful
        if [ $? -eq 0 ]; then
            (echo >&2 "${GOODTOGO} Download successful.")
            
            # Copy the ISO to dockur_storage with the name custom.iso
            cp "$ISO_DIR/$ISO_NAME" "$DOCKUR_STORAGE_DIR/$CUSTOM_ISO_NAME"
            (echo >&2 "${GOODTOGO} ISO copied to dockur_storage as custom.iso.")
        else
            (echo >&2 "${ERROR}  Download failed. Please try again.")
            exit 1
        fi
    else
        (echo >&2 "${INFO} ISO already exists. Skipping download.")
        
        # Copy the ISO to dockur_storage as custom.iso if it's not there already
        if [ ! -f "$DOCKUR_STORAGE_DIR/$CUSTOM_ISO_NAME" ]; then
            cp "$ISO_DIR/$ISO_NAME" "$DOCKUR_STORAGE_DIR/$CUSTOM_ISO_NAME"
            (echo >&2 "${INFO} ISO copied to dockur_storage as custom.iso.")
        else
            (echo >&2 "${INFO} custom.iso already exists in dockur_storage. No action needed.")
        fi
    fi
}
dockur_win_installation(){

    host=$1

    # Check if the variable host contains any of the disallowed values
    if [[ "$host" == "localhost" || "$host" == "127.0.0.1" || "$host" == "host.docker.internal" ]]; then
        (echo >&2 "${ERROR} For windows in docker installation, you must specify the local IP of the host.")
        exit 1
    fi
    
    # Export to env requirements
    export RAM_REQ="17000000" # ~16GB of ram
    export DISK_REQ="50000"  # 50GB of disk 

    # Var used to by setup_box.sh
    export DOCKUR_SETUP=true

    # Check and install requirements
    if $debug_mode; then
        $SETUP_SCRIPT_PATH/requirements.sh 
    else
        $SETUP_SCRIPT_PATH/requirements.sh > /dev/null
    fi

    # OFFLINE MODE in dockur
    if $offline_mode; then
        export COMPOSE_PROFILES="agent-offline,win-offline"
        export DOCKER_CONTAINERS=$(bash "$SETUP_SCRIPT_PATH/parse_docker_compose.sh" agent)

        if $debug_mode; then
            $SETUP_SCRIPT_PATH/setup_docker.sh agent
        else
            $SETUP_SCRIPT_PATH/setup_docker.sh agent > /dev/null
        fi
    else
        # Prepare ISO for dockur
        setup_dockur_win
        export COMPOSE_PROFILES="default,win"
        export DOCKER_CONTAINERS=$(bash "$SETUP_SCRIPT_PATH/parse_docker_compose.sh" agent)

        if $debug_mode; then
            $SETUP_SCRIPT_PATH/setup_docker.sh agent
        else
            $SETUP_SCRIPT_PATH/setup_docker.sh agent > /dev/null
        fi
    fi

    if [ $? -eq 1 ]; then
        (echo >&2 "${ERROR} Failed to launch docker requirements.")
        exit 1
    fi

    # Setup Windows box
    user=vagrant
    password=vagrant
    mount_point="C:" 
    if $debug_mode; then
        $SETUP_SCRIPT_PATH/setup_box.sh $host $user $password $mount_point
    else
        $SETUP_SCRIPT_PATH/setup_box.sh $host $user $password $mount_point > /dev/null
    fi

}

install_from_conf(){
    # Get master host
    master_host=$(get_yml_value "" master_host)
    # Validate IP or FQDN
    if [[ $master_host =~ $ip_regex || $master_host =~ $fqdn_regex ]]; then
        (echo >&2 "${INFO} Valid host string.")
    else
        (echo >&2 "${ERROR} Please enter valid IP or FQDN.")
        exit 0
    fi
    # Setup Master host in env
    export MASTER_IP=$master_host

    # Get location of the windows box to determine installation type
    windows_location=$(get_yml_value "" windows_box_location) # Error in yaml.sh if the key is first arg
    # Get number of cores
    windows_cores=$(get_yml_value "" windows_box_cores)
    export WINDOWS_CORES=$windows_cores

    # Not used for the moment
    # Get Splunk host 
    splunk_host=$(get_yml_value "" splunk_host)
    # Get Splunk user 
    splunk_user=$(get_yml_value "" splunk_user)
    # Get Splunk password 
    splunk_password=$(get_yml_value "" splunk_password)
    # Get Splunk port 
    splunk_port=$(get_yml_value "" splunk_port)
    # Get Splunk management port 
    splunk_mport=$(get_yml_value "" splunk_mport)
    # Get Splunk ssl
    splunk_ssl=$(get_yml_value "" splunk_ssl)

    (echo >&2 "${INFO} Splunk host : $splunk_host")
    (echo >&2 "${INFO} Splunk user : $splunk_user")
    (echo >&2 "${INFO} Splunk password : $splunk_password")
    (echo >&2 "${INFO} Splunk port : $splunk_port")
    (echo >&2 "${INFO} Splunk mport : $splunk_mport")
    (echo >&2 "${INFO} Splunk SSL : $splunk_ssl")

    if [ "$windows_location" = "local" ] ; then 
        local_installation
    elif [ "$windows_location" = "dockur" ] ; then 
        local_agent_host_ip=$(hostname -I | awk '{print $1}')
        # If the master is localhost, use its local IP to avoid Windows using 10.0.2.2 that is only working for Vagrant
        if [[ "$master_host" == "localhost" || "$master_host" == "127.0.0.1" || "$master_host" == "host.docker.internal" ]]; then
            master_host=$local_agent_host_ip
            export MASTER_IP=$master_host
        fi
        dockur_win_installation $local_agent_host_ip
    elif [ "$windows_location" = "remote" ] ; then 
        # Get remote host 
        windows_host=$(get_yml_value "" windows_box_remote_box_host)
        # Get remote user 
        windows_user=$(get_yml_value "" windows_box_remote_box_user)
        # Get remote password 
        windows_password=$(get_yml_value "" windows_box_remote_box_password)
        # Get custom mount point
        windows_mountpoint=$(get_yml_value "" windows_box_remote_box_custom_mountpoint)
        windows_mountpoint="$windows_mountpoint:"
        # Start setup with a remote box
        remote_installation $windows_host $windows_user $windows_password $windows_mountpoint
    else
        (echo >&2 "${ERROR} Wrong location. Needs to be local or remote.")
        exit 0
    fi
}

manual_install(){
    #local_installation

    # Ask user : master host
    default_master_host="127.0.0.1"
    read -p "$(echo -n >&2 "${USERINPUT} Enter the remote master host. [Default is: $default_master_host] [options: IP/FQDN]: ")" master_host
    if [[ -z "$master_host" ]]; then
        master_host="$default_master_host"
    fi
    # Validate IP or FQDN
    if [[ $master_host =~ $ip_regex || $master_host =~ $fqdn_regex ]]; then
        (echo >&2 "${INFO} Valid host string.")
    else
        (echo >&2 "${ERROR} Please enter valid IP or FQDN.")
        exit 0
    fi
    # Setup Master host in env
    export MASTER_IP=$master_host

    # Ask user : local or remote Windows box
    default_location="dockur"
    if is_wsl; then
        USERINPUT_TEXT="${USERINPUT} Do you want to setup a remote Windows machine or setup locally on your Windows host or locally with Windows in docker (dockur) ?"
    else
        USERINPUT_TEXT="${USERINPUT} Do you want to setup a remote Windows machine or setup locally with vbox & vagrant or locally with Windows in docker (dockur) ?"
    fi
    read -p "$(echo -n >&2 "${USERINPUT_TEXT} [Default is: $default_location] [options: local/remote/dockur]: ")" location_type
    # read -p "$(echo -n >&2 "${USERINPUT} Do you want to setup a remote Windows machine or setup locally with vbox & vagrant or locally with windows in docker (dockur) ? [Default is: $default_location] [options: local/remote/dockur]: ")" location_type
    default_win_cores="2"
    read -p "$(echo -n >&2 "${USERINPUT} What is the number of cores of the Windows machine ? [Default is: $default_win_cores]: ")" win_cores
    if [[ -z "$win_cores" ]]; then
        win_cores="$default_win_cores"
    fi
    export WINDOWS_CORES=$win_cores
    if [ "$location_type" = "local" ] ; then
        location_type="local"
        local_installation
        
    elif [ -z "$location_type" ] || [ "$location_type" = "dockur" ] ; then
        location_type="dockur"

        # Get the default local IP address using `hostname -I` and take the first result
        default_ip=$(hostname -I | awk '{print $1}')

        # Prompt for the IP address, showing the default
        read -p "$(echo -n >&2 "${USERINPUT} Enter the IP address of your agent host (required for host <-> docker communication) [default: $default_ip]: ")" windows_host_ip

        # Use the default IP if the user does not enter anything
        windows_host_ip=${windows_host_ip:-$default_ip}

        # Check if the IP address is provided
        if [[ -z "$windows_host_ip" ]]; then
            echo >&2 "${ERROR} Please enter an IP."
            exit 0
        fi

        if [[ $windows_host_ip =~ $ip_regex ]]; then
           (echo >&2 "${INFO} Valid IP.")
        else
            (echo >&2 "${ERROR} Please enter valid IP.")
            exit 0
        fi

        # If the master is localhost, use its local IP to avoid Windows using 10.0.2.2 that is only working for Vagrant
        if [[ "$master_host" == "localhost" || "$master_host" == "127.0.0.1" || "$master_host" == "host.docker.internal" ]]; then
            master_host=$windows_host_ip
            export MASTER_IP=$master_host
        fi

        dockur_win_installation $windows_host_ip
    elif [ "$location_type" = "remote" ] ; then
        # Ask user : remote Windows host IP/FQDN
        default_host="host.docker.internal"
        read -p "$(echo -n >&2 "${USERINPUT} Enter the remote Windows host (WinRM need to be enabled). [Default is: $default_host] [options: IP/FQDN]: ")" host
        # Check if the variable contains an IP address or a FQDN
        if [[ -z "$host" ]]; then
            host="$default_host"
        fi
        if [[ $host =~ $ip_regex || $host =~ $fqdn_regex ]]; then
           (echo >&2 "${INFO} Valid host string.")
        else
            (echo >&2 "${ERROR} Please enter valid IP or FQDN.")
            exit 0
        fi

        # If master host is localhost but Windows is remote, we need to use the IP address, not local host or Windows will try to connect via 10.0.2.2
        if [[ "$master_host" == "localhost" || "$master_host" == "127.0.0.1" || "$master_host" == "host.docker.internal" ]]; then
            (echo >&2 "${ERROR} You are using remote Windows but the master is localhost, you need to specify the real IP address of the master host.")
            exit 0
        fi

        # Ask user : remote Windows host user
        default_user="vagrant"
        read -p "$(echo -n >&2 "${USERINPUT} Enter the remote Windows user (need to be admin). [Default is: $default_user]: ")" user
        if [[ -z "$user" ]]; then
            user="$default_user"
        fi
        # Ask user : remote Windows host password
        default_password="vagrant"
        read -p "$(echo -n >&2 "${USERINPUT} Enter the remote Windows password. [Default is: $default_password]: ")" password
        if [[ -z "$password" ]]; then
            password="$default_password"
        fi
    
        # Ask user : custom mount point on Windows host 
        default_mount="C:"
        read -p "$(echo -n >&2 "${USERINPUT} Enter the custom mount point on the remote Windows for tools installation. [Default is: $default_mount]: ")" mount_point
        if [[ -z "$mount_point" ]]; then
            mount_point="$default_mount"
        fi

        # Start setup with a remote box
        remote_installation $host $user $password $mount_point
    else
        echo $location_type
        (echo >&2 "${ERROR} Please select local or remote")
        exit 0
    fi

    # Ask user : connect agent to Splunk server
    default_connect_splunk="yes"
    read -p "$(echo -n >&2 "${USERINPUT} Do you want to connect agent to a Splunk server ? [Default is: $default_connect_splunk] [options: yes/no]: ")" connect_splunk
    if [ -z "$connect_splunk" ] || [ "$connect_splunk" = "yes" ] ; then

        # Ask user for the Splunk host
        default_splunk_host="host.docker.internal"
        echo "Enter the Splunk Host:"
        echo "  - Press ENTER to use the default Splunk server ($default_splunk_host)"
        echo "  - If using a remote master, enter the FQDN/IP of the remote master"
        echo "  - If you prefer to use a different Splunk server, enter its FQDN/IP."
        read -p "Splunk host [Default: $default_splunk_host]: " splunk_host
        splunk_host=${splunk_host:-$default_splunk_host}

        if [[ -z "$splunk_host" ]]; then
            splunk_host="$default_splunk_host"
        fi

        # Ask user : remote Splunk user
        default_user="admin"
        read -p "$(echo -n >&2 "${USERINPUT} Enter the Splunk user for administration and event forwarding (need to be admin). [Default is: $default_user]: ")" splunk_user
        if [[ -z "$splunk_user" ]]; then
            splunk_user="$default_user"
        fi
        
        # Ask user : remote Splunk password
        default_password="DFIR"
        read -p "$(echo -n >&2 "${USERINPUT} Enter the Splunk password. [Default is: $default_password]: ")" splunk_password
        if [[ -z "$splunk_password" ]]; then
            splunk_password="$default_password"
        fi

        # Ask user : remote Splunk port
        default_splunk_port="8000"
        read -p "$(echo -n >&2 "${USERINPUT} Enter the Splunk port. [Default is: $default_splunk_port]: ")" splunk_port
        if [[ -z "$splunk_port" ]]; then
            splunk_port="$default_splunk_port"
        fi

        # Ask user : remote Splunk management port
        default_splunk_mport="8089"
        read -p "$(echo -n >&2 "${USERINPUT} Enter the Splunk management port. [Default is: $default_splunk_mport]: ")" splunk_mport
        if [[ -z "$splunk_mport" ]]; then
            splunk_mport="$default_splunk_mport"
        fi

        # Ask user : remote Splunk management port
        default_splunk_ssl="False"
        read -p "$(echo -n >&2 "${USERINPUT} Enable SSL for Splunk communication ? . [Default is: $default_splunk_ssl] [options: True/False]: ")" splunk_ssl
        if [[ -z "$splunk_ssl" ]]; then
            splunk_ssl="$default_splunk_ssl"
        fi
    fi

    # Export users input to env
    export LOCATION_TYPE=$location_type
    export WINDOWS_HOST=$host
    export WINDOWS_USER=$user
    export WINDOWS_PASSWORD=$password
    export WINDOWS_MOUNT_POINT=${mount_point//:} # Save drive letter without ":"
    export SPLUNK_REMOTE_HOST=$splunk_host
    export SPLUNK_USER=$splunk_user
    export SPLUNK_PASSWORD=$splunk_password
    export SPLUNK_PORT=$splunk_port
    export SPLUNK_MPORT=$splunk_mport
    export SPLUNK_SSL=$splunk_ssl

    # Save setup config
    conf_agent_sample="$CONF_PATH/agent_sample.yml"
    conf_agent="$CONF_PATH/agent.yml" # CHANGE ME - temporary for dev
    if $debug_mode; then
        $SETUP_SCRIPT_PATH/save_setup_config.sh agent $conf_agent_sample $conf_agent
    else
        $SETUP_SCRIPT_PATH/save_setup_config.sh agent $conf_agent_sample $conf_agent > /dev/null
    fi

}

main() {
    # Check if the script is run as root
    if [ "$EUID" -ne 0 ]; then
        (echo >&2 "${ERROR} This script must be run as root.")
        exit 1
    fi

    # Check if running on WSL
    if is_wsl; then
        # If WSL, check if $WSL_INTEROP is defined
        if [ -z "$WSL_INTEROP" ]; then
            (echo >&2 "${ERROR} \$WSL_INTEROP is not defined. Ensure -E is used with sudo and using WSL.")
            exit 1
        fi
        
        # Add ps1 to path
        WINDOWS_POWERSHELL_PATH="/mnt/c/Windows/System32/WindowsPowerShell/v1.0"
        if ! echo $PATH | grep -q "$WINDOWS_POWERSHELL_PATH"; then
            export PATH="$PATH:$WINDOWS_POWERSHELL_PATH"
        fi

        # Is WSL is not launched as admin, exit
        is_admin=$(powershell.exe -Command "[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)")
        is_admin=$(echo $is_admin | tr -d '\r')

        if [ "$is_admin" != "True" ]; then
            (echo >&2 "${ERROR} WSL must be launched as administrator.")
            exit 1
        fi
    fi

    if [ "$show_help" = true ]; then
        echo "Usage: $0 [-d] [-h]"
        echo "Options:"
        echo "  -d  Enable debug mode"
        echo "  -h  Show this help message"
        echo "  -c  Setup agent from config file. Default is interactive"
        echo "  -o  Offline mode (use prebuilt agent-offline image instead of building locally)"
        exit 0
    fi
    # Install interactive or from config
    if $config_mode; then
        install_from_conf
    else
        manual_install
    fi

}

main
exit 0
