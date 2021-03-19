#!/bin/bash

# Delegate '$DELEGATE_AMOUNT' ro 'VALIDATOR_PUBLIC_KEY_HEX'
# Requirements: 'apt install jq'
# Requirements: '$DELEGATE_AMOUNT' '$VALIDATOR_PUBLIC_KEY_HEX' '$DELEGATOR_PUBLIC_KEY_HEX' '$TARGET_HOST' '$KEY_PATH' '$CONTRACT_PATH' '$CHAIN_NAME' '$payment_amount' 

DELEGATE_AMOUNT="1000"

VALIDATOR_PUBLIC_KEY_HEX=""

DELEGATOR_PUBLIC_KEY_HEX=""

TARGET_HOST="http://127.0.0.1:7777"

KEY_PATH="/etc/casper/validator_keys/secret_key.pem"

CONTRACT_PATH="$HOME/casper-node/target/wasm32-unknown-unknown/release/delegate.wasm"

CHAIN_NAME="delta-11"

payment_amount="1000000000"

casper-client put-deploy --chain-name "$CHAIN_NAME" \
  --node-address "$TARGET_HOST" \
  --secret-key "$KEY_PATH" \
  --session-path  "$HOME/casper-node/target/wasm32-unknown-unknown/release/delegate.wasm" \
  --payment-amount $payment_amount \
  --session-arg="validator:public_key='$VALIDATOR_PUBLIC_KEY_HEX'" \
  --session-arg="amount:u512='$DELEGATE_AMOUNT'" \
  --session-arg="delegator:public_key='$DELEGATOR_PUBLIC_KEY_HEX'"