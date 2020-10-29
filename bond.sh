#!/bin/bash

# Bond validator sequence

BID_AMOUNT="10000"
PROFIT="10"
CHAIN_NAME="casper-testnet-8"
OWNER_PRIVATE_KEY="/etc/casper/validator_keys/secret_key.pem"
API_HOST="http://127.0.0.1:7777"
BONDING_CONTRACT="$HOME/casper-node/target/wasm32-unknown-unknown/release/add_bid.wasm"

RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo && echo -e "Broadcasting bind transaction ..." && echo

TX=$(casper-client put-deploy \
        --chain-name "$CHAIN_NAME" \
        --node-address "$API_HOST" \
        --secret-key "$OWNER_PRIVATE_KEY" \
        --session-path "$BONDING_CONTRACT" \
        --payment-amount '100000000' \
        --session-arg="amount:u512='$BID_AMOUNT'" \
        --session-arg="delegation_rate:u64='$PROFIT'" | jq -r '.result | .deploy_hash')


echo -e "${RED}Transaction hash: ${CYAN}$TX${NC}" && echo

echo -e "${RED}Query transaction ...${NC}" && echo

casper-client get-deploy --node-address "$API_HOST" "$TX" | jq 'del(.result.deploy.session.ModuleBytes.module_bytes)'

echo && echo -e "${RED}Auction status:${NC}" && echo

casper-client get-auction-info --node-address "$API_HOST" | jq

echo && echo -e "${RED}Last added block info:${NC}" && echo

curl -s "$API_HOST"/status | jq .last_added_block_info && echo

