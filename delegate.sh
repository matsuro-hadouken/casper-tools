#!/bin/bash

# Delegate '$DELEGATE_AMOUNT' ro 'VALIDATOR_PUBLIC_KEY_HEX'
# Requirements: 'apt install jq'
# Requirements: 'apt install bc'
# Requirements: '$DELEGATE_AMOUNT' '$VALIDATOR_PUBLIC_KEY_HEX' '$DELEGATOR_PUBLIC_KEY_HEX' '$TARGET_HOST' '$KEY_PATH' '$CONTRACT_PATH' '$CHAIN_NAME' '$payment_amount'

CHAIN_NAME="casper-test" # CHAIN NAME

DELEGATE_AMOUNT="1000000000" # HOW MUCH WE DELEGATE 'IN MOTES'
payment_amount="3000000000"  # TRANSACTION FEE 'IN MOTES'

KEY_PATH="/home/<user>/<folder>/secret_key.pem" # PATH TO DELEGATOR PRIVATE KEY
DELEGATOR_PUBLIC_KEY_HEX="<DELEGATOR_PUBLIC_KEY_HEX>" # DELEGATOR PUBLIC KEY IN HEX FORMAT
VALIDATOR_PUBLIC_KEY_HEX="<VALIDATOR_PUBLIC_KEY_HEX>" # VALIDATOR PUBLIC KEY IN HEX FORMAT
CONTRACT_PATH="$HOME/casper-node/target/wasm32-unknown-unknown/release/delegate.wasm" # PATH TO 'PROPERLY COMPILED' DELEGATION CONTRACT

TARGET_HOST="http://127.0.0.1:7777" # NODE RPC ( CAN BE ANY VALID NODE ON THE SAME NETWORK WITH PORT 7777 OPEN )

# ----------------------------------------------------

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

function ConfirmTransaction() {

  echo && echo -e " ${CYAN}Press 'y' to continue or Ctrl+C to exit.${NC}"

  while true; do

    read -r -n 1 k <&1

    if [[ $k = y ]] ; then

      echo -e "\\r\\033[K${NC}"

      break

    fi

  done

}

function DelegationInfo() {

DELEGATION_AMOUNT_IN_CSPR=$(echo "scale=4; $DELEGATE_AMOUNT / 1000000000" | bc -l)

  echo -e " We about to stake ${GREEN}$DELEGATION_AMOUNT_IN_CSPR CSPR${NC} on validator ${GREEN}$VALIDATOR_PUBLIC_KEY_HEX${NC}"

  ConfirmTransaction

}

function Broadcast() {

TX=$(casper-client put-deploy --chain-name "$CHAIN_NAME" \
        --node-address "$TARGET_HOST" \
        --secret-key "$KEY_PATH" \
        --session-path  "$CONTRACT_PATH" \
        --payment-amount "$payment_amount" \
        --session-arg="validator:public_key='$VALIDATOR_PUBLIC_KEY_HEX'" \
        --session-arg="amount:u512='$DELEGATE_AMOUNT'" \
        --session-arg="delegator:public_key='$DELEGATOR_PUBLIC_KEY_HEX'" | jq -r .result.deploy_hash)

        if [[ "${#TX}" -ne 64 ]]; then

           echo -e " ${RED}Failed to broadcast transaction, exiting ...${NC}" && exit 1
        else
           echo -e " Delegation transaction ID: ${GREEN}$TX${NC}" && echo
        fi

}

function WatchPassTrough() {

  echo -e " Waiting for confirmation ..." && echo

  start=$(date +%s.%N)

  while true; do

    i=1
    sp="▉"
    echo -n ' '
    printf " \\b${sp:i++%${#sp}:1}"

    BlockHash=$(casper-client get-deploy --node-address "$TARGET_HOST" "$TX" | jq -r '.result | .execution_results | .[] | .block_hash')

    if [[ "${#BlockHash}" -eq 64 ]]; then

      duration=$(echo "$(date +%s.%N) - $start" | bc)
      execution_time=$(printf "%.2f seconds" "$duration")

      echo && echo && echo -e " ${CYAN}Confirmed in${NC} $execution_time ${CYAN}seconds, block hash: ${GREEN}$BlockHash${NC}"

      break

    fi

    sleep 10

  done

  echo

}

echo

DelegationInfo

Broadcast

WatchPassTrough
