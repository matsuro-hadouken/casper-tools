#!/bin/bash

# Delegate '$DELEGATE_AMOUNT' ro 'VALIDATOR_PUBLIC_KEY_HEX'
# Requirements: 'apt install jq'
# Requirements: '$DELEGATE_AMOUNT' '$VALIDATOR_PUBLIC_KEY_HEX' '$DELEGATOR_PUBLIC_KEY_HEX' '$TARGET_HOST' '$KEY_PATH' '$CONTRACT_PATH' '$CHAIN_NAME' '$payment_amount' 

DELEGATE_AMOUNT="10000000000"

KEY_PATH="/home/casper/keys/5/secret_key.pem" # PATH TO DELEGATOR PRIVATE KEY

DELEGATOR_PUBLIC_KEY_HEX="<DELEGATOR PUBLIC KEY IN HEX FORMAT>" # DELEGATOR PUBLIC KEY IN HEX FORMAT

VALIDATOR_PUBLIC_KEY_HEX="01a3536b5794be5b53972a9bbb56795cb7a4af385a3f1cddb29e253cbcf73586f6" # VALIDATOR PUBLIC KEY IN HEX FORMAT

TARGET_HOST="http://127.0.0.1:7777" # RPC NODE ADDRESS

CONTRACT_PATH="$HOME/casper-node/target/wasm32-unknown-unknown/release/delegate.wasm" # APPROPRIATELY BUILD DELEGATION CONTRACT

CHAIN_NAME="casper-test" # CHAIN NAME

payment_amount="10000000000" # TRANSACTION FEE ( MOTES )

casper-client put-deploy --chain-name "$CHAIN_NAME" \
  --node-address "$TARGET_HOST" \
  --secret-key "$KEY_PATH" \
  --session-path  "$HOME/casper-node/target/wasm32-unknown-unknown/release/delegate.wasm" \
  --payment-amount $payment_amount \
  --session-arg="validator:public_key='$VALIDATOR_PUBLIC_KEY_HEX'" \
  --session-arg="amount:u512='$DELEGATE_AMOUNT'" \
  --session-arg="delegator:public_key='$DELEGATOR_PUBLIC_KEY_HEX'"
