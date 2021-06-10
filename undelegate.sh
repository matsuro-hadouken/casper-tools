#!/bin/bash

CHAIN_NAME="casper-test"        # CHAIN NAME

UNDELEGATE="1000000000"         # how much to withdraw
payment_amount="1000000000"     # TRANSACTION FEE ( MOTES ) 9 zeros

DELEGATOR_PUBLIC_KEY_HEX="<DELEGATOR_PUBLIC_KEY_HEX>"
VALIDATOR_PUBLIC_KEY_HEX="<VALIDATOR_PUBLIC_KEY_HEX>"

KEY_PATH="/home/casper/delegate/keys/secret_key.pem" # PATH TO 'DELEGATOR' PRIVATE KEY

TARGET_HOST="http://127.0.0.1:7777" # RPC NODE 

CONTRACT_PATH="$HOME/casper-node/target/wasm32-unknown-unknown/release/undelegate.wasm" # PATH TO 'PROPERLY COMPILED' undelegate.wasm

casper-client put-deploy --chain-name "$CHAIN_NAME" \
        --node-address "$TARGET_HOST" \
        --secret-key "$KEY_PATH" \
        --session-path "$CONTRACT_PATH"  \
        --payment-amount "$payment_amount"  \
        --session-arg="delegator:public_key='$DELEGATOR_PUBLIC_KEY_HEX'" \
        --session-arg="validator:public_key='$VALIDATOR_PUBLIC_KEY_HEX'" \
        --session-arg="amount:u512='$UNDELEGATE'"
