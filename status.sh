#!/bin/bash

# Node status monitor

# Matsuro Hadouken <matsuro-hadouken@protonmail.com> 2020
# Contributed By : RapidMark

# This file is free software; as a special exception the author gives
# unlimited permission to copy and/or distribute it, with or without
# modifications, as long as this notice is preserved.

# PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND

# Requirements: 'apt install jq' 'apt install tree'

# When: Run while syncing, or just in general to see the status and messages coming in

# Commands: Ctrl-C to quit

unit_name="casper-node-launcher"

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
NC='\033[0m'

IPv4_STRING='(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'

numba='^[0-9]+$'

theoretically_trusted_ip=$(cat /etc/casper/1_0_0/config.toml | grep 'known_addresses = ' | grep -E -o "$IPv4_STRING")

function watch_unit() {

watch -c SYSTEMD_COLORS=1 "systemctl show casper-node-launcher.service | grep -e MemoryCurrent \
  -e ActiveState \
  -e LoadState \
  -e FragmentPath \
  -e StateChangeTimestamp= && \
  echo && \
  echo "Public signing key: $(curl -s localhost:8888/status | jq .our_public_signing_key)" && echo && \
  echo "Local height:  $(curl -s localhost:8888/status | jq -r .last_added_block_info.height)" && \
  echo "Round length: $(curl -s localhost:8888/status | jq .round_length)" && \
  echo "Next upgrade: $(curl -s localhost:8888/status | jq .next_upgrade)" && \
  echo "Build version: $(curl -s localhost:8888/status | jq .build_version)" && \
  echo "Chain name: $(curl -s localhost:8888/status | jq .chainspec_name)" && \
  echo "Starting state root hash: $(curl -s localhost:8888/status | jq .starting_state_root_hash)" && \
  echo && echo 'Database Size:' && echo && \
  tree --noreport -h --inodes /var/lib/casper/casper-node && echo && \
  echo "Peers connected: $(curl -s localhost:8888/status | jq '.peers | length')" && echo && \
  echo "$(cat /etc/casper/1_0_0/chainspec.toml | grep -e validator_slots)" && echo"



}

watch_unit
