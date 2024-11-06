#!/usr/bin/env bash

ERROR=$(tput setaf 1; echo -n "  [!]"; tput sgr0)
GOODTOGO=$(tput setaf 2; echo -n "  [✓]"; tput sgr0)
INFO=$(tput setaf 3; echo -n "  [-]"; tput sgr0)
USERINPUT=$(tput setaf 4; echo -n "  [?]"; tput sgr0)
MASTER_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

splunk_path="$MASTER_DIR/../splunk/data/"
check_samba(){
    # Run the smbclient command
    #smbclient //192.168.1.77/share -U anonymous -c "ls" --password=""
    sudo docker exec agent-agent sh -c \
        "smbclient //$MASTER_IP/share -U anonymous -c 'ls' --password=''"  #$MASTER_IP from env
    
    status=$?

    # Check if the command was successful
    if [ $status -eq 0 ]; then
        (echo >&2 "${GOODTOGO} Samba share ($MASTER_IP) can be accessed using smbclient from agent-agent.")
        exit 0
    else
        (echo >&2 "${ERROR} Samba share ($MASTER_IP) cannot be accessed using smbclient from agent-agent.")
        exit 1
    fi
}

main() {
    check_samba
}
main