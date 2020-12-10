#!/bin/bash

INPUT_HEX="$1"

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

function checkArguments() {

    if [ -z "$INPUT_HEX" ]; then

        echo && echo -e "${RED}ERROR: Not enough arguments.${NC}" && echo
        echo -e "${GREEN}balance_check.sh <PUBLIC_KEY_HEX>${NC}" && echo

        exit

    fi

    if ! [[ "${#INPUT_HEX}" -eq 66 ]];then

        echo && echo -e "${RED}ERROR: This is probably not a public key ...${NC}" && echo
        echo -e "${GREEN}Check:${NC} cat /etc/casper/validator_keys/public_key_hex" && echo

        exit

    fi

}

function checkBalance() {

echo && echo -e "${CYAN}Input HEX: ${GREEN}$INPUT_HEX${NC}" && echo

LFB=$(curl -s http://127.0.0.1:8888/status | jq -r '.last_added_block_info | .height')

echo -e "${CYAN}Chain height: ${GREEN}$LFB${NC}" && echo

LFB_ROOT=$(casper-client get-block  --node-address http://localhost:7777 -b "$LFB" | jq -r '.result | .block | .header | .state_root_hash')

echo -e "${CYAN}Block ${GREEN}$LFB ${CYAN}state root hash: ${GREEN}$LFB_ROOT${NC}" && echo

PURSE_UREF=$(casper-client query-state --node-address http://localhost:7777 -k "$INPUT_HEX" -s "$LFB_ROOT" | jq -r '.result | .stored_value | .Account | .main_purse')

echo -e "${CYAN}Main purse uref: ${GREEN}$PURSE_UREF${NC}" && echo

BALANCE=$(casper-client get-balance --node-address http://localhost:7777 --purse-uref "$PURSE_UREF" --state-root-hash "$LFB_ROOT" | jq -r '.result | .balance_value')

echo -e "${CYAN}Input balance: ${GREEN}$BALANCE${NC}" && echo

}

