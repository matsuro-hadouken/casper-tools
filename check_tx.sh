#!/bin/bash

# Version: DELTA 7

API='http://127.0.0.1:7777'

TX="$1"

casper-client get-deploy --node-address "$API" "$TX" | jq 'del(.result.deploy.session.ModuleBytes.module_bytes)'
