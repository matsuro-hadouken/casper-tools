#!/bin/bash

# Return validator from deactivated state.
# Requirements: set $chain_name variable
# Requirements: provided keys and contract patch are default, set to setup accordingly.

chain_name="<chain_name>" # 'casper' for main

activate_bid_contract="$HOME/casper-node/target/wasm32-unknown-unknown/release/activate_bid.wasm"
secret_key="/etc/casper/validator_keys/secret_key.pem"
public_key_hex=$(cat /etc/casper/validator_keys/public_key_hex)

casper-client put-deploy --secret-key "$secret_key" \
  --chain-name "$chain_name" \
  --session-path "$activate_bid_contract" \
  --payment-amount 300000000 \
  --session-arg "validator_public_key:public_key='$public_key_hex'"
