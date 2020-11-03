#!/bin/bash

# Check hosts for HTTP availability, count, provide LFB hash.

LOCAL_HTTP_PORT='7777' # if any, if no active validator then doesn't meter

# ------------------------------------------------------------------------

IPv4_STRING='(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo && echo "Counting peers ..." && echo

read -a validators_ip < <(echo $(curl -s http://127.0.0.1:7777/status | jq .peers | grep -E -o "$IPv4_STRING"))

function CountPeers() {

        counter=1

        for i in "${validators_ip[@]}"; do
                ((counter=counter+1))
        done

        # check if run from active validator host, so it will be +1
        if [[ $(curl -s http://127.0.0.1:"$LOCAL_HTTP_PORT"/status | jq -r .api_version) ]]; then
                echo -e "Script run from active validator host, so it will be plus one" && echo
                echo -e "${CYAN}Detected peers: ${NC}$((counter+1))" && echo
        else
                echo -e "${CYAN}Active peers in network: ${NC}$counter" && echo
        fi
}

function main() {

  for i in "${validators_ip[@]}"; do

    validator_lfb_hash=$(curl -s --connect-timeout 2 --max-time 2 http://"$i":7777/status | jq -r '.last_added_block_info | .hash')

    if [[ "${#validator_lfb_hash}" -ne 64 ]]; then

      echo -e "${RED}Bad  -- $i -- Closed HTTP access or dead engine -- -- -- --${NC}"

    else

      echo -e "${GREEN}Good -- $i -- $validator_lfb_hash${NC}"

    fi

  done

}

start=$(date +%s.%N)

CountPeers

main

duration=$(echo "$(date +%s.%N) - $start" | bc)
execution_time=`printf "%.2f seconds" "$duration"`

echo && echo "Check complete in $execution_time seconds." && echo
