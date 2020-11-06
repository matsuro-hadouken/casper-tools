#!/bin/bash

# check peers situation

# THIS IS A MESS FOR NOW, NOTHING FUNCY

IPv4_STRING='(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'

LOCAL_HTTP_PORT='7777' # if any

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

function Seeds() {

  echo && echo -e "Check for trusted hash, going trough seeds ..." && echo

  read -r -a trustedHosts < <(echo $(cat /etc/casper/config.toml | grep 'known_addresses = ' | grep -E -o "$IPv4_STRING"))

  for i in "${trustedHosts[@]}"; do

    trusted_lfb_hash=$(curl -s --connect-timeout 2 --max-time 2 http://"$i":7777/status | jq -r '.last_added_block_info | .hash')
    chain_name_reference=$(curl -s http://"$i":7777/status | jq -r .chainspec_name)

    if [[ "${#trusted_lfb_hash}" -ne 64 ]] && [[ ! "$trusted_lfb_hash" =~ 'null' ]]; then

      echo -e "${RED}Bogus     -- $i -- Closed HTTP access or dead engine -- $validator_lfb_hash -- $chain_name_reference${NC}"

    else
      if [[ "$trusted_lfb_hash" =~ 'null' ]]; then
        trusted_lfb_hash='Waiting for genesis'
      fi

      echo -e "${CYAN}$i${NC} -- ${GREEN}$trusted_lfb_hash${NC} -- ${GREEN}$chain_name_reference${NC}"
    fi

  done
}

function CountPeers() {

  echo && echo "Counting peers ..." && echo

  counter=1

  for i in "${validators_ip[@]}"; do
    ((counter = counter + 1))
  done

  # check if run from active active validator host, so it will be +1
  if [[ $(curl -s http://127.0.0.1:"$LOCAL_HTTP_PORT"/status | jq -r .api_version) ]]; then

    echo -e "Script run from active node host, so it will be plus one" && echo

    host_hash=$(curl -s http:/127.0.0.1:7777/status | jq -r '.last_added_block_info | .hash')
    host_chain_name=$(curl -s http:/127.0.0.1:7777/status | jq -r '.chainspec_name')

    if [[ "$host_chain_name" =~ "$chain_name_reference" ]]; then
      COLOR_CHAIN_NAME='\033[0;32m'
      HOST_STATUS="${GREEN}Awailable${NC}"
    else
      COLOR_CHAIN_NAME='\033[0;31m'
      HOST_STATUS="${RED}Forked${NC}"
    fi

    echo -e "Host: $HOST_STATUS -- ${GREEN}$host_hash -- $COLOR_CHAIN_NAME$host_chain_name${NC}" && echo

    echo -e "${CYAN}Detected peers: ${NC}$((counter + 1))" && echo

  else

    echo -e "${CYAN}Active peers in network: ${NC}$counter" && echo

  fi
}

function main() {

  for i in "${validators_ip[@]}"; do

    validator_lfb_hash=$(curl -s --connect-timeout 2 --max-time 2 http://"$i":7777/status | jq -r '.last_added_block_info | .hash')
    chain_name=$(curl -s http://"$i":7777/status | jq -r .chainspec_name)

    if [[ "$chain_name" =~ "$chain_name_reference" ]]; then
      COLOR_CHAIN_NAME='\033[0;32m'
      HOST_STATUS="${GREEN}Awailable${NC}"
    else
      COLOR_CHAIN_NAME='\033[0;31m'
      HOST_STATUS="${RED}Forked${NC}"
    fi

    if [[ "${#validator_lfb_hash}" -ne 64 ]] && [[ ! "$validator_lfb_hash" =~ "null" ]]; then

      echo -e "${RED}Bogus  -- $i -- Closed HTTP access or dead engine -- -- $validator_lfb_hash${NC} -- $COLOR_CHAIN_NAME$chain_name${NC}"

    else

      if [[ "$trusted_lfb_hash" =~ 'Waiting for genesis' ]]; then

        if [[ "$validator_lfb_hash" =~ 'null' ]]; then

          echo -e "${GREEN}Waiting for genesis -- $i${NC} -- $COLOR_CHAIN_NAME$chain_name${NC}"

        else

          echo -e "${RED}Fork    -- $i -- $validator_lfb_hash${NC} -- $COLOR_CHAIN_NAME$chain_name${NC}"

        fi

      fi

      if ! [[ "$trusted_lfb_hash" =~ 'Waiting for genesis' ]]; then

        if [[ "${#validator_lfb_hash}" -ne 64 ]]; then

          echo -e "${RED}Bogus  -- $i -- Closed HTTP access or dead engine -- -- $validator_lfb_hash${NC} -- $COLOR_CHAIN_NAME$chain_name${NC}"

        else

          echo -e "$HOST_STATUS -- $i -- ${GREEN}$validator_lfb_hash${NC} -- $COLOR_CHAIN_NAME$chain_name${NC}"

        fi

      fi

    fi

  done

}

start=$(date +%s.%N)

read -r -a validators_ip < <(echo $(curl -s http://127.0.0.1:7777/status | jq .peers | grep -E -o "$IPv4_STRING"))

Seeds

CountPeers

main

duration=$(echo "$(date +%s.%N) - $start" | bc)
execution_time=$(printf "%.2f seconds" "$duration")

echo && echo "Check complete in $execution_time seconds." && echo
