#!/bin/bash

# Tested and works on "delta-11"

# Bond validat to networks
# Requirements: 'apt install jq'
# Requirements: Set 'validator public hex' , 'BID_AMOUNT' , 'PROFIT ( fee ), 'CHAIN_NAME', 'OWNER_PRIVATE_KEY' path, 'API' end pint, 'BONDING_CONTRACT' path.

PUB_KEY_HEX="$1"

BID_AMOUNT="12345678"
payment_amount="3000000"
validator_comission="10"

CHAIN_NAME=`curl -s localhost:8888/status | jq -r .chainspec_name`
public_hex_path='/etc/casper/validator_keys/public_key_hex'
OWNER_PRIVATE_KEY="/etc/casper/validator_keys/secret_key.pem"
API_HOST="http://127.0.0.1:7777"
BONDING_CONTRACT="$HOME/casper-node/target/wasm32-unknown-unknown/release/add_bid.wasm"

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'


function GetPublicHEX() {

    AutoHEX=$(cat "$public_hex_path")

    if [ -z "$PUB_KEY_HEX" ]; then
        PUB_KEY_HEX="$AutoHEX"
        echo && echo -e "${RED}No valid manual input detected !${NC}" && echo
        echo -e "Using public HEX from: ${RED}$public_hex_path${NC}"
    fi

    echo && echo -e "Public HEX: ${CYAN}$PUB_KEY_HEX${NC}"

}

GetPublicHEX

echo && echo -e "Broadcasting, chain name:  ${CYAN}$CHAIN_NAME${NC} ..." && echo

TX=$(casper-client put-deploy \
        --chain-name "$CHAIN_NAME" \
        --node-address "$API_HOST" \
        --secret-key "$OWNER_PRIVATE_KEY" \
        --session-path "$BONDING_CONTRACT" \
        --payment-amount "$payment_amount" \
        --session-arg="public_key:public_key='$PUB_KEY_HEX'" \
        --session-arg="amount:u512='$BID_AMOUNT'" \
        --session-arg="delegation_rate:u8='$validator_comission'" | jq -r '.result | .deploy_hash')

