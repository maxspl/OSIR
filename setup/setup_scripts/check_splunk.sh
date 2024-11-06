#!/usr/bin/env bash

ERROR=$(tput setaf 1; echo -n "  [!]"; tput sgr0)
GOODTOGO=$(tput setaf 2; echo -n "  [✓]"; tput sgr0)
INFO=$(tput setaf 3; echo -n "  [-]"; tput sgr0)
USERINPUT=$(tput setaf 4; echo -n "  [?]"; tput sgr0)
MASTER_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

splunk_path="$MASTER_DIR/../splunk/data/"
check_splunk_install(){
    if [ -d "$splunk_path" ]; then
        file_count=$(find "$splunk_path" -type f | wc -l)
    else
        file_count=0
    fi
    # Check if the file count is greater than zero
    if [ "$file_count" -gt 0 ]; then
        (echo >&2 "${INFO} $splunk_path contains files, a Splunk was previously installed.")
        exit 1
    else
        (echo >&2 "${INFO} $splunk_path does not contain file, Splunk can be installed.")
    fi
}

main() {
    check_splunk_install 
}
main