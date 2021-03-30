#!/bin/bash

# test tool, requirements: 'apt install jq && apt install bc'

sleep_time=0.58 # sleep interval [0.58] is about 100 transaction per minute.

GAS="10000" # mandatory gas value, this is not refundable in any case and absolute minimum. 

DESTINATION_ADDRESS="DESTINATION_PUB_HEX" # we will send transaction this direction

AMOUNT='2500000000' # This is minimum amount which can be send for now ( minimum requirement for input activation )

deploysCount=1 # how many deploys we about to push

TTL='30m'

CHAIN_NAME="casper-dryrun" # chain name, match mandatory.

TARGET_HOST="127.0.0.1" # Target. In case target is remote machine, please consider latency when setting up $sleep_time

API="http://$TARGET_HOST:7777" # port probably standard, but just in case check.

OWNER_ADDRESS="$(cat /home/casper/test_key/public_key_hex)" # check path
OWNER_PRIVATE_KEY='/home/casper/test_key/secret_key.pem'    # check path

# nothing much to change below

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

function send_transaction_ttl() {

TX=$(casper-client transfer \
                --node-address "$API" \
                --secret-key "$OWNER_PRIVATE_KEY" \
                -a "$AMOUNT" \
                -t "$DESTINATION_ADDRESS" \
                -p "$GAS" \
                --chain-name "$CHAIN_NAME" \
                --ttl="$TTL" | jq -r '.result | .deploy_hash')

}

start=$(date +%s.%N) # start time check

for run in $(seq "$deploysCount"); do

        send_transaction_ttl && sleep "$sleep_time"
        echo -e "${CYAN}Transaction hash: ${GREEN}$TX${NC}"

done

duration=$(echo "$(date +%s.%N) - $start" | bc)
execution_time=$(printf "%.2f seconds" "$duration")

echo -e "${RED}Execution Time: $execution_time${NC}"
