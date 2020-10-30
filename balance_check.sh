#!/bin/bash

# Check input balance
# Requirements: 'apt install jq'
# Requirements: `Provide Public Key Hex` in to `INPUT_HEX` variable below.

INPUT_HEX='PUBLIC_KEY_HEX'

# -----------------------------------------------------------------------

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo && echo -e "${CYAN}Input HEX: ${GREEN}$INPUT_HEX${NC}" && echo

# Get chain heigh
LFB=$(curl -s http://127.0.0.1:7777/status | jq -r '.last_added_block_info | .height')

echo -e "${CYAN}Chain height: ${GREEN}$LFB${NC}" && echo

# 1) Get LFB state root hash
LFB_ROOT=$(casper-client get-block  --node-address http://localhost:7777 -b "$LFB" | jq -r '.result | .block | .header | .state_root_hash')

echo -e "${CYAN}Block ${GREEN}$LFB ${CYAN}state root hash: ${GREEN}$LFB_ROOT${NC}" && echo

# 2) Get purse UREF
PURSE_UREF=$(casper-client query-state --node-address http://localhost:7777 -k "$INPUT_HEX" -g "$LFB_ROOT" | jq -r '.result | .stored_value | .Account | .main_purse')

echo -e "${CYAN}Main purse uref: ${GREEN}$PURSE_UREF${NC}" && echo

# 3) Found balance
BALANCE=$(casper-client get-balance --node-address http://localhost:7777 --purse-uref "$PURSE_UREF" --state-root-hash "$LFB_ROOT" | jq -r '.result | .balance_value')

echo -e "${CYAN}Input balance: ${GREEN}$BALANCE${NC}" && echo
