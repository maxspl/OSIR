#!/usr/bin/env bash

ERROR=$(tput setaf 1; echo -n "  [!]"; tput sgr0)
GOODTOGO=$(tput setaf 2; echo -n "  [✓]"; tput sgr0)
INFO=$(tput setaf 3; echo -n "  [-]"; tput sgr0)
USERINPUT=$(tput setaf 4; echo -n "  [?]"; tput sgr0)
MASTER_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

splunk_data="$MASTER_DIR/../splunk/data/*/*"
clean_splunk_data(){
    rm -rf $splunk_data
    (echo >&2 "${INFO} files in $splunk_data erased.")
}

main() {
    clean_splunk_data 
}
main