#!/bin/bash

# Coming to Delta-11, 'not tested yet'

# Propose validator bid.

# Requirements: 'apt install jq'
# Requirements: 'add_bid.wasm' should be compiled according instruction. Current 'Delta 11' target 'v0.9.3'
# Requirements: 'BID AMOUNT', 'validator comission', 'CHAIN NAME', 'OWNER PRIVATE KEY PATH', 'TARGET IP', 'ADD BID WASM PATH'.

# Note the path to files and keys. Note: the 'session arguments need to be encased in double-quotes', with the 'parameter values in single quotes'.
# Note the required payment amount. It must contain 'at least 10 zeros'. The payment amount is specified 'in motes'.

PUB_KEY_HEX="$(cat /etc/casper/validator_keys/public_key_hex)"
BID_AMOUNT="1234567890"

payment_amount="10000000000"

validator_comission="10"
CHAIN_NAME="delta-11"
OWNER_PRIVATE_KEY="/etc/casper/validator_keys/secret_key.pem"
API_HOST="http://127.0.0.1:7777"
BONDING_CONTRACT="$HOME/casper-node/target/wasm32-unknown-unknown/release/add_bid.wasm"

RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo && echo -e "Deploy ..." && echo

TX=$(casper-client put-deploy \
        --chain-name "$CHAIN_NAME" \
        --node-address "$API_HOST" \
        --secret-key "$OWNER_PRIVATE_KEY" \
        --session-path "$BONDING_CONTRACT" \
        --payment-amount "$payment_amount" \
        --session-arg="public_key:public_key='$PUB_KEY_HEX'" \
        --session-arg="amount:u512='$BID_AMOUNT'" \
        --session-arg="delegation_rate:u64='$validator_comission'" | jq -r '.result | .deploy_hash')

sleep 2 && echo -e "${RED}Transaction hash: ${CYAN}$TX${NC}" && echo
