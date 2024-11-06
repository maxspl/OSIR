#!/usr/bin/env bash

ERROR=$(tput setaf 1; echo -n "  [!]"; tput sgr0)
GOODTOGO=$(tput setaf 2; echo -n "  [✓]"; tput sgr0)
INFO=$(tput setaf 3; echo -n "  [-]"; tput sgr0)
USERINPUT=$(tput setaf 4; echo -n "  [?]"; tput sgr0)

save_agent_setup_conf() {
    cp $conf_sample $conf
    sed -i "s/{master_host}/$MASTER_IP/g" $conf
    sed -i "s/{windows_box_location}/$LOCATION_TYPE/g" $conf
    sed -i "s/{windows_box_cores}/$WINDOWS_CORES/g" $conf
    sed -i "s/{windows_box_remote_box_host}/$WINDOWS_HOST/g" $conf
    sed -i "s/{windows_box_remote_box_user}/$WINDOWS_USER/g" $conf
    sed -i "s/{windows_box_remote_box_password}/$WINDOWS_PASSWORD/g" $conf
    sed -i "s/{windows_box_remote_box_custom_mountpoint}/$WINDOWS_MOUNT_POINT/g" $conf
    sed -i "s/{splunk_host}/$SPLUNK_REMOTE_HOST/g" $conf
    sed -i "s/{splunk_user}/$SPLUNK_USER/g" $conf
    sed -i "s/{splunk_password}/$SPLUNK_PASSWORD/g" $conf
    sed -i "s/{splunk_port}/$SPLUNK_PORT/g" $conf
    sed -i "s/{splunk_mport}/$SPLUNK_MPORT/g" $conf
    sed -i "s/{splunk_ssl}/$SPLUNK_SSL/g" $conf
    
    # Return the exit status of the last command executed
    return $?
}

save_master_setup_conf() {
    cp $conf_sample $conf
    sed -i "s/{splunk_location}/$SPLUNK_LOCATION/g" $conf
    sed -i "s/{splunk_user}/$SPLUNK_USER/g" $conf
    sed -i "s/{splunk_password}/$SPLUNK_PASSWORD/g" $conf
    sed -i "s/{splunk_remote_splunk_host}/$SPLUNK_REMOTE_HOST/g" $conf
    sed -i "s/{splunk_port}/$SPLUNK_PORT/g" $conf
    sed -i "s/{splunk_mport}/$SPLUNK_MPORT/g" $conf
    sed -i "s/{splunk_ssl}/$SPLUNK_SSL/g" $conf

    # Return the exit status of the last command executed
    return $?
}

main() {
    
    if [ "$type" = "agent" ] ; then  
        if save_agent_setup_conf; then
            (echo >&2 "${GOODTOGO} Manual configuration saved to $conf.")
        else
            (echo >&2 "${ERROR} Failed to save configuration to $conf.")
        fi
    elif [ "$type" = "master" ] ; then  
        if save_master_setup_conf; then
            (echo >&2 "${GOODTOGO} Manual configuration saved to $conf.")
        else
            (echo >&2 "${ERROR} Failed to save configuration to $conf.")
        fi
    fi
}

type=$1 # master or agent
conf_sample=$2
conf=$3
main $type $conf_sample $conf
exit 0
