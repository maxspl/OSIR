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
keep_elastic_data=true # If set, install ElasticSearch without erasing previous data
erase_elastic=false # If set, ElasticSearch data is erased for new installation

# Docker compose profiles are accumulated in two arrays so that base profiles
# and per-SIEM profiles can be built in any order without one clobbering the
# other (previously a single COMPOSE_PROFILES string was overwritten by
# build_base_profiles if called after the SIEM installers, which was a
# fragile, order-dependent pattern).
declare -a OSIR_BASE_PROFILES=()
declare -a OSIR_SIEM_PROFILES=()

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

    # Read keep/erase flags from environment (set by install_from_conf or manual_install)
    local keep_splunk_data="${KEEP_SPLUNK_DATA:-true}"
    local erase_splunk="${ERASE_SPLUNK:-false}"

    # If not a fresh install, erase previous Splunk data or stop installation
    if [ "$keep_splunk_data" != "true" ]; then
        if [ "$erase_splunk" = "true" ]; then
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

    # Append the splunk profile to the SIEM profile array (joined into
    # COMPOSE_PROFILES by launch_docker_stack, order-independent).
    if $offline_mode; then
        add_siem_profile "splunk-offline"
    else
        add_siem_profile "splunk-online"
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

    # Remote Splunk: no local container is launched. The base docker stack
    # (master/rabbitmq/redis/...) is launched once by the caller.

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


local_es_installation(){
    # Export to env requirements
    export RAM_REQ="8000000" # ~8GB of ram
    export DISK_REQ="100000"  # 100GB of disk

    # Check and install requirements
    if $debug_mode; then
        $SETUP_SCRIPT_PATH/requirements.sh
    else
        $SETUP_SCRIPT_PATH/requirements.sh > /dev/null
    fi

    # Ensure elastic data directory exists with correct ownership for the
    # elasticsearch container user (uid 1000)
    ES_DATA_DIR=$(realpath "$MASTER_DIR/../../setup/elastic/data")
    mkdir -p "$ES_DATA_DIR"
    chown -R 1000:1000 "$ES_DATA_DIR"

    # Read keep/erase flags from environment (set by install_from_conf or manual_install)
    local keep_es_data="${KEEP_ELASTIC_DATA:-true}"
    local erase_es="${ERASE_ELASTIC:-false}"

    # If not a fresh install, erase previous ElasticSearch data or stop installation
    if [ "$keep_es_data" != "true" ]; then
        if [ "$erase_es" = "true" ]; then
            # Erase ElasticSearch data
            if $debug_mode; then
                $SETUP_SCRIPT_PATH/clean_elastic.sh
            else
                $SETUP_SCRIPT_PATH/clean_elastic.sh > /dev/null
            fi
        else 
            (echo >&2 "${ERROR} Erase data ElasticSearch is not set, stopping execution.")
            exit 0
        fi
    fi

    # Append the elasticsearch profile to the SIEM profile array (joined into
    # COMPOSE_PROFILES by launch_docker_stack, order-independent).
    if $offline_mode; then
        add_siem_profile "elasticsearch-offline"
    else
        add_siem_profile "elasticsearch-online"
    fi
}

remote_es_installation(){
    # No local container for remote ElasticSearch; nothing to launch here.
    es_host=$1
    es_user=$2
    es_password=$3
    es_port=$4
    es_ssl=$5

    echo "es_host : $es_host" > /dev/null
    echo "es_user : $es_user" > /dev/null
    echo "es_password : $es_password" > /dev/null
    echo "es_port : $es_port" > /dev/null
    echo "es_ssl : $es_ssl" > /dev/null
}


build_base_profiles(){
    # Build the common profiles array (master/rabbitmq/redis/samba) without any
    # SIEM. Can be called before or after the SIEM installers: it only ever
    # touches OSIR_BASE_PROFILES, never OSIR_SIEM_PROFILES.
    if $offline_mode; then
        if is_wsl; then
            OSIR_BASE_PROFILES=("default-offline" "master-offline")
        else
            OSIR_BASE_PROFILES=("default-offline" "master-offline" "smb-offline")
        fi
    else
        if is_wsl; then
            OSIR_BASE_PROFILES=("default" "master-online")
        else
            OSIR_BASE_PROFILES=("default" "master-online" "smb-online")
        fi
    fi
}

add_siem_profile(){
    # Append a SIEM-specific docker compose profile (e.g. "splunk-online").
    # Kept separate from OSIR_BASE_PROFILES so build_base_profiles can be
    # called in any order relative to the SIEM installers.
    OSIR_SIEM_PROFILES+=("$1")
}

launch_docker_stack(){
    # Join the accumulated base + SIEM profiles into COMPOSE_PROFILES and
    # launch the full docker stack once.
    local all_profiles=("${OSIR_BASE_PROFILES[@]}" "${OSIR_SIEM_PROFILES[@]}")
    export COMPOSE_PROFILES=$(IFS=,; echo "${all_profiles[*]}")

    export DOCKER_CONTAINERS=$(bash "$SETUP_SCRIPT_PATH/parse_docker_compose.sh" master)
    if $debug_mode; then
        $SETUP_SCRIPT_PATH/setup_docker.sh master
    else
        $SETUP_SCRIPT_PATH/setup_docker.sh master > /dev/null
    fi
    if [ $? -eq 1 ]; then
        (echo >&2 "${ERROR} Failed to launch Docker containers.")
        exit 1
    fi
}


install_from_conf(){
    # Determine which SIEM(s) to deploy
    siem_selected=$(get_yml_value "" siem_selected)
    if [ -z "$siem_selected" ]; then
        siem_selected="splunk"
    fi

    # Build the base (non-SIEM) docker profiles. Order relative to the
    # SIEM installers below no longer matters (see build_base_profiles).
    build_base_profiles

    # --- Splunk (if selected) ---
    if [ "$siem_selected" = "splunk" ] || [ "$siem_selected" = "both" ]; then
        splunk_location=$(get_yml_value "" splunk_location)
        # Initialize keep/erase flags
        keep_splunk_data=true
        erase_splunk=false
        if [ "$splunk_location" = "local" ] ; then
            if $debug_mode; then
                $SETUP_SCRIPT_PATH/check_splunk.sh
            else
                $SETUP_SCRIPT_PATH/check_splunk.sh > /dev/null
            fi
            if [ $? -eq 1 ]; then
                keep_splunk_data=false
                splunk_data=$(get_yml_value "" local_splunk_previous_data)
                if [ "$splunk_data" = "keep" ] ; then
                    keep_splunk_data=true
                elif [ "$splunk_data" = "erase" ] ; then
                    erase_splunk=true
                fi
            fi
            export KEEP_SPLUNK_DATA=$keep_splunk_data
            export ERASE_SPLUNK=$erase_splunk
            local_splunk_installation
        elif [ "$splunk_location" = "remote" ] ; then
            splunk_host=$(get_yml_value "" splunk_remote_splunk_host)
            splunk_user=$(get_yml_value "" splunk_user)
            splunk_password=$(get_yml_value "" splunk_password)
            splunk_port=$(get_yml_value "" splunk_port)
            splunk_mport=$(get_yml_value "" splunk_mport)
            splunk_ssl=$(get_yml_value "" splunk_ssl)
            remote_splunk_installation $splunk_host $splunk_user $splunk_password $splunk_port $splunk_mport $splunk_ssl
        else
            (echo >&2 "${ERROR} Wrong splunk location. Needs to be local or remote.")
            exit 0
        fi
    fi

    # --- ElasticSearch (if selected) ---
    if [ "$siem_selected" = "elasticsearch" ] || [ "$siem_selected" = "both" ]; then
        es_location=$(get_yml_value "" elasticsearch_location)
        # Initialize keep/erase flags
        keep_elastic_data=true
        erase_elastic=false
        if [ "$es_location" = "local" ] ; then
            if $debug_mode; then
                $SETUP_SCRIPT_PATH/check_elastic.sh
            else
                $SETUP_SCRIPT_PATH/check_elastic.sh > /dev/null
            fi
            if [ $? -eq 1 ]; then
                keep_elastic_data=false
                elastic_data=$(get_yml_value "" local_es_previous_data)
                if [ "$elastic_data" = "keep" ] ; then
                    keep_elastic_data=true
                elif [ "$elastic_data" = "erase" ] ; then
                    erase_elastic=true
                fi
            fi
            export KEEP_ELASTIC_DATA=$keep_elastic_data
            export ERASE_ELASTIC=$erase_elastic
            local_es_installation
        elif [ "$es_location" = "remote" ] ; then
            es_host=$(get_yml_value "" elasticsearch_remote_es_host)
            es_user=$(get_yml_value "" elasticsearch_user)
            es_password=$(get_yml_value "" elasticsearch_password)
            es_port=$(get_yml_value "" elasticsearch_port)
            es_ssl=$(get_yml_value "" elasticsearch_ssl)
            remote_es_installation $es_host $es_user $es_password $es_port $es_ssl
        else
            (echo >&2 "${ERROR} Wrong elasticsearch location. Needs to be local or remote.")
            exit 0
        fi
        kibana_port=$(get_yml_value "" kibana_port)
    fi

# Persist SIEM choice and ES values for the agent/master config
    export SIEM_SELECTED=$siem_selected
    export ELASTIC_LOCATION=${es_location:-remote}
    export ELASTIC_HOST=${es_host:-127.0.0.1}
    export ELASTIC_PORT=${es_port:-9200}
    export ELASTIC_USER=${es_user:-elastic}
    export ELASTIC_PASSWORD=${es_password:-DFIR_passwd}
    export ELASTIC_SSL=${es_ssl:-False}
    export ELASTIC_REMOTE_HOST=${es_host:-127.0.0.1}
    export KIBANA_PORT=${kibana_port:-5601}
    export KEEP_ELASTIC_DATA=$keep_elastic_data
    export ERASE_ELASTIC=$erase_elastic
    export KEEP_SPLUNK_DATA=$keep_splunk_data
    export ERASE_SPLUNK=$erase_splunk

    # Launch the accumulated stack (base + SIEM profiles already appended)
    launch_docker_stack
}

manual_install(){
    # 1) Choose which SIEM to deploy
    default_siem="splunk"
    read -p "$(echo -n >&2 "${USERINPUT} Which SIEM do you want to use for visualization ? [Default is: $default_siem] [options: splunk/elasticsearch/both]: ")" siem_selected
    if [[ -z "$siem_selected" ]]; then
        siem_selected="$default_siem"
    fi
    siem_selected=$(echo "$siem_selected" | tr '[:upper:]' '[:lower:]')
    if [[ "$siem_selected" != "splunk" && "$siem_selected" != "elasticsearch" && "$siem_selected" != "both" ]]; then
        (echo >&2 "${ERROR} Invalid SIEM choice. Use splunk, elasticsearch or both.")
        exit 0
    fi

    # Build the base (non-SIEM) docker profiles. Order relative to the
    # SIEM installers below no longer matters (see build_base_profiles).
    build_base_profiles

    # 2) Configure Splunk if selected
    if [ "$siem_selected" = "splunk" ] || [ "$siem_selected" = "both" ]; then
        read -p "$(echo -n >&2 "${USERINPUT} Setup a local Splunk server or configure a remote one ? [Default is: local] [options: local/remote]: ")" splunk_location
        if [[ -z "$splunk_location" ]]; then splunk_location="local"; fi

        default_user="admin"
        read -p "$(echo -n >&2 "${USERINPUT} Enter the Splunk user (need to be admin). [Default is: $default_user]: ")" splunk_user
        if [[ -z "$splunk_user" ]]; then splunk_user="$default_user"; fi

        default_password="DFIR_passwd"
        read -p "$(echo -n >&2 "${USERINPUT} Enter the Splunk password. [Default is: $default_password]: ")" splunk_password
        if [[ -z "$splunk_password" ]]; then splunk_password="$default_password"; fi

        default_splunk_port="8000"
        read -p "$(echo -n >&2 "${USERINPUT} Enter the Splunk web port. [Default is: $default_splunk_port]: ")" splunk_port
        if [[ -z "$splunk_port" ]]; then splunk_port="$default_splunk_port"; fi

        default_splunk_mport="8089"
        read -p "$(echo -n >&2 "${USERINPUT} Enter the Splunk management port. [Default is: $default_splunk_mport]: ")" splunk_mport
        if [[ -z "$splunk_mport" ]]; then splunk_mport="$default_splunk_mport"; fi

        default_splunk_ssl="False"
        read -p "$(echo -n >&2 "${USERINPUT} Enable SSL for Splunk communication ? [Default is: $default_splunk_ssl] [options: True/False]: ")" splunk_ssl
        if [[ -z "$splunk_ssl" ]]; then splunk_ssl="$default_splunk_ssl"; fi

        if [ "$splunk_location" = "local" ] ; then
            splunk_host="127.0.0.1"
            # Initialize keep/erase flags
            keep_splunk_data=true
            erase_splunk=false
            if $debug_mode; then
                $SETUP_SCRIPT_PATH/check_splunk.sh
            else
                $SETUP_SCRIPT_PATH/check_splunk.sh > /dev/null
            fi
            if [ $? -eq 1 ]; then
                keep_splunk_data=false
                default_choice=stop
                read -p "$(echo -n >&2 "${USERINPUT} Splunk data found. continue (keep) / erase / stop ? [Default is: $default_choice] [options: stop/continue/erase]: ")" user_choice
                if [[ -z "$user_choice" ]]; then user_choice="$default_choice"; fi
                if [ "$user_choice" = "continue" ]; then keep_splunk_data=true; elif [ "$user_choice" = "erase" ]; then erase_splunk=true; fi
            fi
            export KEEP_SPLUNK_DATA=$keep_splunk_data
            export ERASE_SPLUNK=$erase_splunk
            local_splunk_installation
        else
            default_splunk_host="host.docker.internal"
            read -p "$(echo -n >&2 "${USERINPUT} Enter the Splunk host. [Default is: $default_splunk_host] [options: IP/FQDN]: ")" splunk_host
            if [[ -z "$splunk_host" ]]; then splunk_host="$default_splunk_host"; fi
            if [[ ! $splunk_host =~ $ip_regex && ! $splunk_host =~ $fqdn_regex ]]; then
                (echo >&2 "${ERROR} Please enter valid IP or FQDN.")
                exit 0
            fi
            remote_splunk_installation $splunk_host $splunk_user $splunk_password $splunk_port $splunk_mport $splunk_ssl
        fi
    fi

    # 3) Configure ElasticSearch if selected
    if [ "$siem_selected" = "elasticsearch" ] || [ "$siem_selected" = "both" ]; then
        read -p "$(echo -n >&2 "${USERINPUT} Setup a local ElasticSearch server or configure a remote one ? [Default is: local] [options: local/remote]: ")" es_location
        if [[ -z "$es_location" ]]; then es_location="local"; fi

        default_es_user="elastic"
        read -p "$(echo -n >&2 "${USERINPUT} Enter the ElasticSearch user. [Default is: $default_es_user]: ")" es_user
        if [[ -z "$es_user" ]]; then es_user="$default_es_user"; fi

        default_es_password="DFIR_passwd"
        read -p "$(echo -n >&2 "${USERINPUT} Enter the ElasticSearch password. [Default is: $default_es_password]: ")" es_password
        if [[ -z "$es_password" ]]; then es_password="$default_es_password"; fi

        default_es_port="9200"
        read -p "$(echo -n >&2 "${USERINPUT} Enter the ElasticSearch REST port. [Default is: $default_es_port]: ")" es_port
        if [[ -z "$es_port" ]]; then es_port="$default_es_port"; fi

        default_es_ssl="False"
        read -p "$(echo -n >&2 "${USERINPUT} Enable SSL for ElasticSearch communication ? [Default is: $default_es_ssl] [options: True/False]: ")" es_ssl
        if [[ -z "$es_ssl" ]]; then es_ssl="$default_es_ssl"; fi

        default_kibana_port="5601"
        read -p "$(echo -n >&2 "${USERINPUT} Enter the Kibana web port. [Default is: $default_kibana_port]: ")" kibana_port
        if [[ -z "$kibana_port" ]]; then kibana_port="$default_kibana_port"; fi

        if [ "$es_location" = "local" ] ; then
            es_host="127.0.0.1"
            # Initialize keep/erase flags
            keep_elastic_data=true
            erase_elastic=false
            if $debug_mode; then
                $SETUP_SCRIPT_PATH/check_elastic.sh
            else
                $SETUP_SCRIPT_PATH/check_elastic.sh > /dev/null
            fi
            if [ $? -eq 1 ]; then
                keep_elastic_data=false
                default_choice=stop
                read -p "$(echo -n >&2 "${USERINPUT} ElasticSearch data found. continue (keep) / erase / stop ? [Default is: $default_choice] [options: stop/continue/erase]: ")" user_choice
                if [[ -z "$user_choice" ]]; then user_choice="$default_choice"; fi
                if [ "$user_choice" = "continue" ]; then keep_elastic_data=true; elif [ "$user_choice" = "erase" ]; then erase_elastic=true; fi
            fi
            export KEEP_ELASTIC_DATA=$keep_elastic_data
            export ERASE_ELASTIC=$erase_elastic
            local_es_installation
        else
            default_es_host="host.docker.internal"
            read -p "$(echo -n >&2 "${USERINPUT} Enter the ElasticSearch host. [Default is: $default_es_host] [options: IP/FQDN]: ")" es_host
            if [[ -z "$es_host" ]]; then es_host="$default_es_host"; fi
            if [[ ! $es_host =~ $ip_regex && ! $es_host =~ $fqdn_regex ]]; then
                (echo >&2 "${ERROR} Please enter valid IP or FQDN.")
                exit 0
            fi
            remote_es_installation $es_host $es_user $es_password $es_port $es_ssl
        fi
    fi

    # 4) Export users input to env
    export SIEM_SELECTED=$siem_selected
    export SPLUNK_LOCATION=$splunk_location
    export SPLUNK_USER=$splunk_user
    export SPLUNK_PASSWORD=$splunk_password
    export SPLUNK_REMOTE_HOST=$splunk_host
    export SPLUNK_PORT=$splunk_port
    export SPLUNK_MPORT=$splunk_mport
    export SPLUNK_SSL=$splunk_ssl
    export ELASTIC_LOCATION=$es_location
    export ELASTIC_HOST=$es_host
    export ELASTIC_USER=$es_user
    export ELASTIC_PASSWORD=$es_password
    export ELASTIC_PORT=$es_port
    export ELASTIC_SSL=$es_ssl
    export ELASTIC_REMOTE_HOST=$es_host
    export KIBANA_PORT=${kibana_port:-5601}

    # Persist previous data choice for local SIEMs
    if [ "$splunk_location" = "local" ]; then
        if $keep_splunk_data; then
            export LOCAL_SPLUNK_PREVIOUS_DATA="keep"
        elif $erase_splunk; then
            export LOCAL_SPLUNK_PREVIOUS_DATA="erase"
        else
            export LOCAL_SPLUNK_PREVIOUS_DATA="stop"
        fi
    fi

    if [ "$es_location" = "local" ]; then
        if $keep_elastic_data; then
            export LOCAL_ELASTIC_PREVIOUS_DATA="keep"
        elif $erase_elastic; then
            export LOCAL_ELASTIC_PREVIOUS_DATA="erase"
        else
            export LOCAL_ELASTIC_PREVIOUS_DATA="stop"
        fi

        export KEEP_ELASTIC_DATA=$keep_elastic_data
        export ERASE_ELASTIC=$erase_elastic
    fi

    if [ "$splunk_location" = "local" ]; then
        export KEEP_SPLUNK_DATA=$keep_splunk_data
        export ERASE_SPLUNK=$erase_splunk
    fi

    # 5) Launch the accumulated stack (base + SIEM profiles already appended)
    launch_docker_stack

    # 6) Save setup config
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