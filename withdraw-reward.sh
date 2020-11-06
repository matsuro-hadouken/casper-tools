#!/bin/bash

# reward withdraw

# Requirements: DELTA 1 master branch contracts ('make build-contracts-rs release')
# Requirements: 'apt install jq'
# Requirements: 'path to smart contract` and 'validator public hex` below

VALIDATOR_PUB_HEX='VALIDATOR_PUB_HEX'

withdraw_validator_reward_contract="$HOME/casper-node/target/wasm32-unknown-unknown/release/withdraw_validator_reward.wasm"

API='http://localhost:7777' # set to another point if necessary

# ------------------------------------------------------------------------------------------------------------------------

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

function Broadcast() {

  echo && echo -e "Deploying withdrawal transaction ..." && echo

  TX=$(casper-client put-deploy \
    --chain-name casper-delta-1 \
    --node-address "$API" \
    -k /etc/casper/validator_keys/secret_key.pem \
    --session-path "$withdraw_validator_reward_contract" \
    --payment-amount 1000000000 \
    --session-arg "validator_public_key:public_key='$VALIDATOR_PUB_HEX'" \
    --session-arg "target_purse:opt_uref=null" | jq -r '.result | .deploy_hash')

  echo -e "Transaction ID: ${GREEN}$TX${NC}" && echo

  WatchPassTrough

}

function WatchPassTrough() {

  echo -e "Waiting for confirmation ..." && echo

  start=$(date +%s.%N)

  while true; do

    i=1
    sp="▉"
    echo -n ' '
    printf "\b${sp:i++%${#sp}:1}"

    BlockHash="$(casper-client get-deploy --node-address http://127.0.0.1:7777 $TX | jq -r '.result | .execution_results | .[] | .block_hash')"

    if [[ "${#BlockHash}" -eq 64 ]]; then

      duration=$(echo "$(date +%s.%N) - $start" | bc)
      execution_time=`printf "%.2f seconds" "$duration"`

      echo && echo && echo -e "${CYAN}Confirmed in${NC} $execution_time ${CYAN}seconds, block hash: ${GREEN}$BlockHash${NC}" && echo

      CheckTX

    fi

    sleep 1

  done

}

function CheckTX() {

  echo -e "Query transaction data ..." && echo

  casper-client get-deploy --node-address http://127.0.0.1:7777 "$TX" | jq 'del(.result.deploy.session.ModuleBytes.module_bytes)'

  exit 0

}

Broadcast
