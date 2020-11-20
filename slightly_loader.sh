#!/bin/bash

# Requirements: 'apt install jq'
# Requirements: Feed 'SPARE_ADDRESS' for gas, set publix HEX and key path for both.
# Requirements: Set appropriate 'CHAIN_NAME'

AMOUNT='10101' # coins to send each transaction
SPAM_EACH='2'  # how much transactions to push trough each host ( minimum 2 )

LOOP_TIMES='0' # how many times repeat all the process ( 0 = no repeat )

CHAIN_NAME="casper-delta-3"

# Big bag:
MAIN_ADDRESS='<MAIN_BAG_HEX_ADDRESS>'
MAIN_PRIVATE_KEY='/etc/casper/validator_keys/secret_key.pem'

# Spare address:
SPARE_ADDRESS='<SPARE_INPUT_HEX>'
SPARE_PRIVATE_KEY="$HOME/scripts/keys/secret_key.pem"

# -------------------------------------------------------------------------------

IPv4_STRING='(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

read -a validators_ip < <(echo $(curl -s http://127.0.0.1:7777/status | jq .peers | grep -E -o "$IPv4_STRING"))

function main() {

  for i in "${validators_ip[@]}"; do

    validator_lfb_hash=$(curl -s http://"$i":7777/status | jq -r '.last_added_block_info | .hash')

    if [[ "${#validator_lfb_hash}" -ne 64 ]]; then

      echo && echo -e "${RED}Host $i blocked port 7777 or whatever${NC}"

    else

      echo && echo -e "${CYAN}Deploy trough $i${NC}" && echo

      PingPong "$i"

    fi

  done

}

function PingPong() {

  start=$(date +%s.%N) # start time check

  for run in $(seq "$burst"); do

    casper-client transfer \
      --node-address "http://$1:7777" \
      --secret-key "$MAIN_PRIVATE_KEY" \
      -a "$AMOUNT" \
      -t "$SPARE_ADDRESS" \
      -p 10000000000000 \
      --chain-name "$CHAIN_NAME" | jq '.result | .deploy_hash'

    casper-client transfer \
      --node-address "http://$1:7777" \
      --secret-key "$SPARE_PRIVATE_KEY" \
      --target-account "$MAIN_ADDRESS" \
      --payment-amount 10000000000000 \
      --amount "$AMOUNT" \
      --chain-name "$CHAIN_NAME" | jq '.result | .deploy_hash'

  done

  duration=$(echo "$(date +%s.%N) - $start" | bc)
  execution_time=$(printf "%.2f seconds" $duration)

  echo && echo "Execution Time: $execution_time"

}

burst=$(expr "$SPAM_EACH" / 2)

if [[ "$LOOP_TIMES" -eq 0 ]]; then

  main

else

  for run in $(seq "$LOOP_TIMES"); do

    main && echo

    echo -e "${CYAN}================================================${NC}"
    echo -e "${RED}PASS TROUGH ALL ACTIVE PEERS, STARTING AGAIN ...${NC}"
    echo -e "${CYAN}================================================${NC}"

  done

fi

echo
