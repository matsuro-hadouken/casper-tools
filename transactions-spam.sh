#!/bin/bash

OWNER_ADDRESS='target_account_one_HEX_STRING'
OWNER_PRIVATE_KEY='/path/to/first/secret_key.pem'

TEST_ADDRESS='target_account_two_HEX_STRING'
TEST_PRIVATE_KEY='/path/to/second/secret_key.pem'

function send_to_test() {

    casper-client transfer \
        --node-address http://127.0.0.1:7777 \
        --secret-key "$OWNER_PRIVATE_KEY" \
        --target-account "$TEST_ADDRESS" \
        --payment-amount 100000000 \
        --amount 100000000 \
        --chain-name casper-charlie-testnet-1

    echo

}

function send_to_owner() {

    casper-client transfer \
        --node-address http://127.0.0.1:7777 \
        --secret-key "$TEST_PRIVATE_KEY" \
        --target-account "$OWNER_ADDRESS" \
        --payment-amount 100000000 \
        --amount 100000000 \
        --chain-name casper-charlie-testnet-1

    echo

}


for run in {1..3}

   do

        send_to_test

        send_to_owner

   done
