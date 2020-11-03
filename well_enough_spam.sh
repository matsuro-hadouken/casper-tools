#!/bin/bash

# it will send funds from address A to address B

# Requirements: 'apt install jq`
# Requirements: Setup all variables below
# Requirements: Need two inputs with provate keys under control, set appropriate path for both.

# Exemple of use: './well_enough_spam.sh <target_host_ip>'
# Example of use: './well_enough_spam.sh 127.0.0.1'

AMOUNT='101'# how much coins will be send each transaction

deploysCount=1 # how many transaction will be send

TTL='1m'

CHAIN_NAME="casper-testnet-8"

# Main bag from where we send
OWNER_ADDRESS='<MAIN_ADDRESS_BIG_BAG_HEX>'
OWNER_PRIVATE_KEY='/etc/casper/validator_keys/secret_key.pem'

# Destination address
DESTINATION_ADDRESS="<DESTINATION_ADDRESS_HEX>"

# ------------------------------------------------------------------------------------

TARGET_HOST="$1"
API="http://$TARGET_HOST:7777"

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

function send_transaction() {

TX=$(casper-client transfer \
                --node-address $API \
                --secret-key "$OWNER_PRIVATE_KEY" \
                -a "$AMOUNT" \
                -t "$DESTINATION_ADDRESS" \
                -p 10000000000000 \
                --chain-name "$CHAIN_NAME" \
                --ttl="$TTL" | jq -r '.result | .deploy_hash')

}

start=$(date +%s.%N) # start time check

for run in $(seq "$deploysCount"); do

        send_transaction
        echo -e "${CYAN}Transaction hash: ${GREEN}$TX${NC}"

done

duration=$(echo "$(date +%s.%N) - $start" | bc)
execution_time=`printf "%.2f seconds" $duration`

echo && echo -e "${RED}Execution Time: $execution_time${NC}" && echo
