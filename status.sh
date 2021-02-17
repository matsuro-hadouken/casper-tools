#!/bin/bash

# Contributed By : RapidMark

# Monitor the status of yor node

# Requirements: 'apt install jq'

# When: Run while syncing, or just in general to see the status and messages coming in

# Commands: Ctrl-C to quit

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
NC='\033[0m'

watch \
	-c  SYSTEMD_COLORS=1 \
	"systemctl status casper-node-launcher.service && \
	printf '\n' && \
	df && \
	printf '\n' && \
	echo 'height (you / current): $GREEN`curl -s localhost:8888/status | jq -r .last_added_block_info.height`$NC / $GREEN `curl -s 18.144.176.168:8888/status | jq -r .last_added_block_info.height`$NC' && \
	echo 'Last Block: $GREEN`date --date=$(curl -s localhost:8888/status | jq -r .last_added_block_info.timestamp)`$NC' &&\
	echo 'Local DB Size: $GREEN`du -h /var/lib/casper/casper-node/ | cut -f 1`$NC' &&
	printf '\n' && \
	sudo tail /var/log/casper/casper-node.log"


