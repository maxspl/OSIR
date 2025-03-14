#!/usr/bin/env bash

# 1. Enter interactive (by default) or automated configuration depending on option selected by user
# 2. Check if splunk if remote or local
# 3. Get Splunk user and password
# 4. If splunk is local :
#     - check if a Splunk installation was previously done (check files in ../splunk/data/)
#     - If a previous install was done : check if user chose to erase, keep data or stop the installation
#     - Install or start again Splunk docker:
#         - Check requirements (docker, disk, ram)
#         - Erase data, do nothing or Stop execution according to selection
#         - Run all dockers (master, samba, splunk) including Splunk
# 5. If splunk is remote :
    # - Get splunk host
    # - Check requirements (docker, disk, ram)
    # - Run all dockers (master, samba) except Splun

ERROR=$(tput setaf 1; echo -n "  [!]"; tput sgr0)
GOODTOGO=$(tput setaf 2; echo -n "  [✓]"; tput sgr0)
INFO=$(tput setaf 3; echo -n "  [-]"; tput sgr0)
USERINPUT=$(tput setaf 4; echo -n "  [?]"; tput sgr0)
MASTER_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
SETUP_SCRIPT_PATH=$(realpath "$MASTER_DIR/../setup_scripts")
CONF_PATH=$(realpath "$MASTER_DIR/../conf")
SHARE_PATH=$(realpath "$MASTER_DIR/../../share")
debug_mode=true
config_mode=false # If set, nothing is ask to the user. Configuration is pulled from agent.yml
offline_mode=false  # OFFLINE MODE FLAG
keep_splunk_data=true # If set, install Splunk without erasing previous data
erase_splunk=false # If set, Splunk data is erased for new installation

# Regular expression to match an IP address
ip_regex='^([0-9]{1,3}\.){3}[0-9]{1,3}$'
# Regular expression to match an FQDN
fqdn_regex='^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


# Parse command line arguments
while getopts "hdco" arg; do   # ADD "o" FOR OFFLINE
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
    o)  # OFFLINE MODE
      offline_mode=true
      ;;
    *)
      echo "Unknown argument: $arg"
      exit 1
      ;;
  esac
done

get_yml_value(){
    source $SETUP_SCRIPT_PATH/yaml.sh
    parse_yaml $CONF_PATH/master.yml | grep $2 | grep -oP '"(.*)"' | tr -d '"'
}

is_wsl() {
    if grep -q "microsoft" /proc/version; then
        (echo >&2 "${INFO} Wsl detected, smb docker not launched")
        return 0   # true
    else
        return 1   # false
    fi
}



local_splunk_installation(){
    # Export to env requirements
    export RAM_REQ="17000000" # ~16GB of ram
    export DISK_REQ="150000"  # 150GB of disk

    # Check and install requirements
    if $debug_mode; then
        $SETUP_SCRIPT_PATH/requirements.sh
    else
        $SETUP_SCRIPT_PATH/requirements.sh > /dev/null
    fi

    # If not a fresh install, erase previous Splunk data or stop installation
    if ! $keep_splunk_data; then
        if $erase_splunk; then
            # Erase Splunk data
            if $debug_mode; then
                $SETUP_SCRIPT_PATH/clean_splunk.sh
            else
                $SETUP_SCRIPT_PATH/clean_splunk.sh > /dev/null
            fi
        else 
            (echo >&2 "${ERROR} Erase data Splunk is not set, stopping execution.")
            exit 0
        fi
    fi

    # Launch docker

    if $offline_mode; then
        if is_wsl; then
            export COMPOSE_PROFILES="default-offline,master-offline,splunk-offline"  
        else
            export COMPOSE_PROFILES="default-offline,master-offline,splunk-offline,smb-offline"
        fi
    else
        if is_wsl; then
            export COMPOSE_PROFILES="default,master-online,splunk-online"
        else
            export COMPOSE_PROFILES="default,master-online,splunk-online,smb-online"
        fi
    fi

    export DOCKER_CONTAINERS=$(bash "$SETUP_SCRIPT_PATH/parse_docker_compose.sh" master)
    if $debug_mode; then
        $SETUP_SCRIPT_PATH/setup_docker.sh master
    else
        $SETUP_SCRIPT_PATH/setup_docker.sh master > /dev/null
    fi

    if [ $? -eq 1 ]; then
        (echo >&2 "${ERROR} Failed to launch Docker containers for local Splunk.")
        exit 1
    fi  
}

remote_splunk_installation(){
    # Export to env requirements
    export RAM_REQ="17000000" # ~16GB of ram
    export DISK_REQ="150000"  # 150GB of disk

    # Check and install requirements
    if $debug_mode; then
        $SETUP_SCRIPT_PATH/requirements.sh
    else
        $SETUP_SCRIPT_PATH/requirements.sh > /dev/null
    fi

    # Launch docker

    # OFFLINE check
    if $offline_mode; then
        if is_wsl; then
            # Maybe no samba in WSL
            export COMPOSE_PROFILES="default-offline,master-offline"
        else
            export COMPOSE_PROFILES="default-offline,master-offline,smb-offline"
        fi
    else
        if is_wsl; then
            export COMPOSE_PROFILES="default,master-online"
        else
            export COMPOSE_PROFILES="default,master-online,smb-online"
        fi
    fi


    export DOCKER_CONTAINERS=$(bash "$SETUP_SCRIPT_PATH/parse_docker_compose.sh" master)
    if $debug_mode; then
        $SETUP_SCRIPT_PATH/setup_docker.sh master
    else
        $SETUP_SCRIPT_PATH/setup_docker.sh master > /dev/null
    fi
    # Check exit code
    if [ $? -eq 1 ]; then
        (echo >&2 "${ERROR} Failed to launch docker requirements.")
        exit 1
    fi

    splunk_host=$1
    splunk_user=$2
    splunk_password=$3
    splunk_port=$4
    splunk_mport=$5
    splunk_ssl=$6
    
    echo "splunk_host : $splunk_host" > /dev/null
    echo "splunk_user : $splunk_user" > /dev/null
    echo "splunk_password : $splunk_password" > /dev/null
    echo "splunk_port : $splunk_port" > /dev/null
    echo "splunk_mport : $splunk_mport" > /dev/null
    echo "splunk_ssl : $splunk_ssl" > /dev/null
}


install_from_conf(){
    # Get location of the windows box to determine installation type
    splunk_location=$(get_yml_value "" splunk_location) # Error in yaml.sh if the key is first arg
    if [ "$splunk_location" = "local" ] ; then 
        
        # Check if Splunk was previously installed
        if $debug_mode; then
            $SETUP_SCRIPT_PATH/check_splunk.sh 
        else
            $SETUP_SCRIPT_PATH/check_splunk.sh > /dev/null
        fi
        # Check exit code: if enter condition if previous data found
        if [ $? -eq 1 ]; then
            keep_splunk_data=false
            
            # Get instruction if data present from previous installation
            splunk_data=$(get_yml_value "" local_splunk_previous_data)
            if [ "$splunk_data" = "keep" ] ; then 
                keep_splunk_data=true
            elif [ "$splunk_data" = "erase" ] ; then 
                erase_splunk=true
            fi
        fi
        local_splunk_installation
    elif [ "$splunk_location" = "remote" ] ; then 
        # Get Splunk host 
        splunk_host=$(get_yml_value "" splunk_remote_splunk_host)
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

        # Start setup with a remote Splunk
        remote_splunk_installation $splunk_host $splunk_user $splunk_password $splunk_port $splunk_mport $splunk_ssl
    else
        (echo >&2 "${ERROR} Wrong location. Needs to be local or remote.")
        exit 0
    fi
}

manual_install(){
    #local_installation

    # Ask user : local or remote splunk
    default_location="local"
    read -p "$(echo -n >&2 "${USERINPUT} Do you want to setup a local Splunk server or configure a remote one ? [Default is: $default_location] [options: local/remote]: ")" splunk_location
    
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

    # Setup local Splunk server
    if [ -z "$splunk_location" ] || [ "$splunk_location" = "local" ] ; then
        splunk_location="local"
        splunk_host="127.0.0.1"
        
        # Check if Splunk was previously installed
        if $debug_mode; then
            $SETUP_SCRIPT_PATH/check_splunk.sh 
        else
            $SETUP_SCRIPT_PATH/check_splunk.sh > /dev/null
        fi
        # Check exit code: if enter condition if previous data found
        if [ $? -eq 1 ]; then
            keep_splunk_data=false
            # Ask user : proceed Splunk installation and erase files or stop installation
            default_choice=stop
            read -p "$(echo -n >&2 "${USERINPUT} To continue Splunk installation, select continue if you want to restart the same instance or erase for fresh new install. [Default is: $default_choice] [options: stop/continue/erase]: ")" user_choice
            if [[ -z "$user_choice" ]]; then
                user_choice="$default_choice"
            
            elif [ "$user_choice" = "continue" ]; then
                keep_splunk_data=true
            
            elif [ "$user_choice" = "erase" ]; then
                erase_splunk=true
            fi
        fi
        local_splunk_installation $splunk_user $splunk_password $splunk_port $splunk_mport $splunk_ssl

    elif [ "$splunk_location" = "remote" ] ; then
        # Ask user : remote Splunk host IP/FQDN
        default_splunk_host="host.docker.internal"
        read -p "$(echo -n >&2 "${USERINPUT} Enter the Splunk host. [Default is: $default_splunk_host] [options: IP/FQDN]: ")" splunk_host
        
        # Check if the variable contains an IP address or a FQDN
        if [[ -z "$splunk_host" ]]; then
            splunk_host="$default_splunk_host"
        fi
        if [[ $splunk_host =~ $ip_regex || $splunk_host =~ $fqdn_regex ]]; then
           (echo >&2 "${INFO} Valid host string.")
        else
            echo "splunk_host : $splunk_host"
            (echo >&2 "${ERROR} Please enter valid IP or FQDN.")
            exit 0
        fi

        # Start setup with remote splunk server
        remote_splunk_installation $splunk_host $splunk_user $splunk_password $splunk_port $splunk_mport $splunk_ssl
    else
        (echo >&2 "${ERROR} Please select local or remote")
        exit 0
    fi

    # Export users input to env
    export SPLUNK_LOCATION=$splunk_location
    export SPLUNK_USER=$splunk_user
    export SPLUNK_PASSWORD=$splunk_password
    export SPLUNK_REMOTE_HOST=$splunk_host
    export SPLUNK_PORT=$splunk_port
    export SPLUNK_MPORT=$splunk_mport
    export SPLUNK_SSL=$splunk_ssl

    # Save setup config
    conf_master_sample="$CONF_PATH/master_sample.yml"
    conf_master="$CONF_PATH/master.yml" # CHANGE ME - temporary for dev
    if $debug_mode; then
        $SETUP_SCRIPT_PATH/save_setup_config.sh master $conf_master_sample $conf_master
    else
        $SETUP_SCRIPT_PATH/save_setup_config.sh master $conf_master_sample $conf_master > /dev/null
    fi

}

main() {
    # Setup Master IP in env
    export MASTER_IP=$(hostname -I | awk '{print $1}')
    echo "${INFO} MASTER IP = $MASTER_IP"

    # Check if the script is run as root
    if [ "$EUID" -ne 0 ]; then
        (echo >&2 "${ERROR} This script must be run as root.")
        exit 1
    fi
    if [ "$show_help" = true ]; then
        echo "Usage: $0 [-d] [-h]"
        echo "Options:"
        echo "  -d  Enable debug mode"
        echo "  -h  Show this help message"
        echo "  -c  Setup master from config file. Default is interactive"
    echo "  -o  Offline mode (use master-offline, splunk-offline, samba-offline, etc.)"
        exit 0
    fi
    # Install interactive or from config
    if $config_mode; then
        install_from_conf
    else
        manual_install
    fi

    # Create a file used be remote agent to check if samba access is working
    touch $SHARE_PATH/smb_test_file 

}

main
exit 0

# 1. Setup docker 
# 2. 

# COMPOSE_PROFILES=frontend,debug docker compose up