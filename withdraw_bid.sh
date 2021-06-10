#!/bin/bash

CHAIN_NAME="casper-test" # CHAIN NAME

WITHDRAW_AMOUNT="10000000000" # how much we withdraw
payment_amount="1000000000" # TRANSACTION FEE ( MOTES ) 9 zeros

VALIDATOR_PUB_HEX=$(cat /etc/casper/validator_keys/public_key_hex) # VALIDATOR_PUB_HEX
SECRET_KEY_PATH="/etc/casper/validator_keys/secret_key.pem"        # PATH TO 'SECRET_KEY'

TARGET_HOST="http://127.0.0.1:7777" # RPC NODE 

CONTRACT_PATH="$HOME/casper-node/target/wasm32-unknown-unknown/release/withdraw_bid.wasm" # PATH TO 'PROPERLY BUILD' withdraw_bid.wasm 

casper-client put-deploy --chain-name "$CHAIN_NAME" \
        --node-address "$TARGET_HOST" \  
        --secret-key "$SECRET_KEY_PATH" \ 
        --session-path "$CONTRACT_PATH"  \   
        --payment-amount "$payment_amount"  \
        --session-arg="public_key:public_key='$VALIDATOR_PUB_HEX'" \
        --session-arg="amount:u512='$WITHDRAW_AMOUNT'" \
        --session-arg="unbond_purse:opt_uref=null"
