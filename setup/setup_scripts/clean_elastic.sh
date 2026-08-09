#!/usr/bin/env bash

ERROR=$(tput setaf 1; echo -n "  [!]"; tput sgr0)
GOODTOGO=$(tput setaf 2; echo -n "  [✓]"; tput sgr0)
INFO=$(tput setaf 3; echo -n "  [-]"; tput sgr0)
USERINPUT=$(tput setaf 4; echo -n "  [?]"; tput sgr0)
MASTER_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

elastic_data="$MASTER_DIR/../../setup/elastic/data/*/*"
clean_elastic_data(){
    rm -rf $elastic_data
    (echo >&2 "${INFO} files in $elastic_data erased.")
    # Ensure the data directory exists with correct ownership for the ES container.
    ES_DIR=$(realpath "$MASTER_DIR/../../setup/elastic/data")
    mkdir -p "$ES_DIR"
    chown -R 1000:1000 "$ES_DIR"
}

main() {
    clean_elastic_data 
}
main