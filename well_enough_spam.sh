#!/bin/bash

# Version: Delta-3

# it will send funds from address A to address B

# Requirements: 'apt install jq`
# Requirements: Setup all variables below
# Requirements: Need two inputs, keys, set appropriate path for both.

# Exemple of use: './well_enough_spam.sh <target_host_ip>'
# Example of use: './well_enough_spam.sh 127.0.0.1'

#!/bin/bash

# we will spam in to this HEX
DESTINATION_ADDRESS="<DESTINATION_ADDRESS>"

# Funds will be spend from here
OWNER_ADDRESS='<BIG_BAG_ADDRESS>'
OWNER_PRIVATE_KEY='/etc/casper/validator_keys/secret_key.pem'

AMOUNT='111'

GAS="1000000000"

# How many deploys ?
deploysCount=1

TTL='1m'

CHAIN_NAME="casper-delta-3"

TARGET_HOST="$1"

# --------------------------------------------------------------------------------

API="http://$TARGET_HOST:7777"

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

function send_transaction() {

    TX=$(casper-client transfer \
        --node-address "$API" \
        --secret-key "$OWNER_PRIVATE_KEY" \
        -a "$AMOUNT" \
        -t "$DESTINATION_ADDRESS" \
        -p "$GAS" \
        --chain-name "$CHAIN_NAME" | jq -r '.result | .deploy_hash')
}

start=$(date +%s.%N) # start time check

for run in $(seq "$deploysCount"); do

    send_transaction_ttl
    echo -e "${CYAN}Transaction hash: ${GREEN}$TX${NC}"

done

duration=$(echo "$(date +%s.%N) - $start" | bc)
execution_time=$(printf "%.2f seconds" $duration)

echo && echo -e "${RED}Execution Time: $execution_time${NC}" && echo
