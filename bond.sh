#!/bin/bash

# Coming to Delta-11, 'not tested yet'

# Propose validator bid.

<<<<<<< HEAD
PUB_KEY_HEX="$1"

BID_AMOUNT="978000000000"
GAS="1000000000" # So far this is minimum which I be able to achive, 10 zeros
=======
# Requirements: 'apt install jq'
# Requirements: 'add_bid.wasm' should be compiled according instruction. Current 'Delta 11' target 'v0.9.3'
# Requirements: 'BID AMOUNT', 'validator comission', 'CHAIN NAME', 'OWNER PRIVATE KEY PATH', 'TARGET IP', 'ADD BID WASM PATH'.

# Note the path to files and keys. Note: the 'session arguments need to be encased in double-quotes', with the 'parameter values in single quotes'.
# Note the required payment amount. It must contain 'at least 10 zeros'. The payment amount is specified 'in motes'.

PUB_KEY_HEX="$(cat /etc/casper/validator_keys/public_key_hex)"
BID_AMOUNT="1234567890"
>>>>>>> upstream/master

payment_amount="10000000000"

<<<<<<< HEAD
CHAIN_NAME=`curl -s localhost:8888/status | jq -r .chainspec_name`
public_hex_path='/etc/casper/validator_keys/public_key_hex'
=======
validator_comission="10"
CHAIN_NAME="delta-11"
>>>>>>> upstream/master
OWNER_PRIVATE_KEY="/etc/casper/validator_keys/secret_key.pem"
API_HOST="http://127.0.0.1:7777"
BONDING_CONTRACT="$HOME/casper-node/target/wasm32-unknown-unknown/release/add_bid.wasm"

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

<<<<<<< HEAD

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

echo && echo -e "Broadcasting bind transaction for ${CYAN}$CHAIN_NAME${NC}..." && echo
=======
echo && echo -e "Deploy ..." && echo
>>>>>>> upstream/master

TX=$(casper-client put-deploy \
        --chain-name "$CHAIN_NAME" \
        --node-address "$API_HOST" \
        --secret-key "$OWNER_PRIVATE_KEY" \
        --session-path "$BONDING_CONTRACT" \
<<<<<<< HEAD
        --payment-amount "$GAS" \
        --session-arg=public_key:"public_key='$PUB_KEY_HEX'" \
        --session-arg=amount:"u512='$BID_AMOUNT'" \
        --session-arg=delegation_rate:"u8='$PROFIT'" | jq -r '.result | .deploy_hash')

echo -e "${RED}Transaction hash: ${CYAN}$TX${NC}" && echo
=======
        --payment-amount "$payment_amount" \
        --session-arg="public_key:public_key='$PUB_KEY_HEX'" \
        --session-arg="amount:u512='$BID_AMOUNT'" \
        --session-arg="delegation_rate:u8='$validator_comission'" | jq -r '.result | .deploy_hash')
>>>>>>> upstream/master

sleep 2 && echo -e "${RED}Transaction hash: ${CYAN}$TX${NC}" && echo
