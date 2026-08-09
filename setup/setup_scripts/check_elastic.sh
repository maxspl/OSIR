#!/usr/bin/env bash

ERROR=$(tput setaf 1; echo -n "  [!]"; tput sgr0)
GOODTOGO=$(tput setaf 2; echo -n "  [✓]"; tput sgr0)
INFO=$(tput setaf 3; echo -n "  [-]"; tput sgr0)
USERINPUT=$(tput setaf 4; echo -n "  [?]"; tput sgr0)
MASTER_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

elastic_path="$MASTER_DIR/../../setup/elastic/data/"
check_elastic_install(){
    if [ -d "$elastic_path" ]; then
        file_count=$(find "$elastic_path" -type f | wc -l)
    else
        file_count=0
    fi
    # Check if the file count is greater than zero
    if [ "$file_count" -gt 0 ]; then
        (echo >&2 "${INFO} $elastic_path contains files, ElasticSearch was previously installed.")
        exit 1
    else
        (echo >&2 "${INFO} $elastic_path does not contain file, ElasticSearch can be installed.")
    fi
}

main() {
    check_elastic_install 
}
main