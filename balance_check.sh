#!/bin/bash

# Version: DELTA 11

# Check input balance
# Requirements: 'apt install jq'
# Instruction:  'balance_check.sh <PUBLIC_KEY_HEX>'

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

public_hex_path='/etc/casper/validator_keys/public_key_hex'
INPUT_HEX="$1"

TARGET_HOST="127.0.0.1"

function GetPublicHEX() {

    AutoHEX=$(cat "$public_hex_path")

    if [ -z "$INPUT_HEX" ]; then
        INPUT_HEX="$AutoHEX"
        echo && echo -e "${RED}No valid manual input detected !${NC}" && echo
        echo -e "Using public HEX from: ${RED}$public_hex_path${NC}"
    fi

    echo && echo -e "Public HEX: ${CYAN}$INPUT_HEX${NC}"

}

function checkBalance() {

echo && echo -e "${CYAN}Input HEX: ${GREEN}$INPUT_HEX${NC}" && echo

LFB=$(curl -s http://$TARGET_HOST:8888/status | jq -r '.last_added_block_info | .height')

echo -e "${CYAN}Chain height: ${GREEN}$LFB${NC}" && echo

LFB_ROOT=$(casper-client get-block  --node-address http://$TARGET_HOST:7777 -b "$LFB" | jq -r '.result | .block | .header | .state_root_hash')

echo -e "${CYAN}Block ${GREEN}$LFB ${CYAN}state root hash: ${GREEN}$LFB_ROOT${NC}" && echo

PURSE_UREF=$(casper-client query-state --node-address http://$TARGET_HOST:7777 -k "$INPUT_HEX" -s "$LFB_ROOT" | jq -r '.result | .stored_value | .Account | .main_purse')

echo -e "${CYAN}Main purse uref: ${GREEN}$PURSE_UREF${NC}" && echo

BALANCE=$(casper-client get-balance --node-address http://$TARGET_HOST:7777 --purse-uref "$PURSE_UREF" --state-root-hash "$LFB_ROOT" | jq -r '.result | .balance_value')

echo -e "${CYAN}Input balance: ${GREEN}$BALANCE${NC}" && echo

}

GetPublicHEX

checkBalance
