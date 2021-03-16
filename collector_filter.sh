#!/bin/bash

# To make it functional need IP database, collected by crawler which is a separate script
# https://github.com/matsuro-hadouken/casper-tools/blob/master/Big_Brother.sh

# IP filter, need to change name of the print function in 'dead_or_alive', currently set to 'build_config' line 21
# 'dead_or_alive' function feed with "big.brother" database collected by network crawler script line 23
# available functions: 'print_all', 'print_good', 'print_good_ip_only', 'build_config', 'print_bad' set on line 21

format=" %-15s %-14s %-14s\n"

STATUS_PORT='8888'

numba='^[0-9]+$'

function dead_or_alive() {

  while IFS= read -r peer_ip; do

  readarray -t era_plus_height < <(curl -s --max-time 10 --connect-timeout 10 http://"$peer_ip":"$STATUS_PORT"/status | jq -r '.last_added_block_info | .era_id,.height')

  peer_era="${era_plus_height[0]}"
  peer_height="${era_plus_height[1]}"

  build_config

  done <"big.brother"

}

function print_all() {

  if ! [[ "$peer_height" =~ $numba ]]; then
    printf "$format" "$peer_ip" "- DEAD -"
  else
    printf "$format" "$peer_ip" "Era: $peer_era" "Height: $peer_height"
  fi

}

function print_good() {

  if [[ "$peer_height" =~ $numba ]]; then
    printf "$format" "$peer_ip" "Era: $peer_era" "Height: $peer_height"
  fi

}

function print_good_ip_only() {

  if [[ "$peer_height" =~ $numba ]]; then
    echo "$peer_ip"
  fi

}

function build_config() {

  if [[ "$peer_height" =~ $numba ]]; then

     if [[ "$peer_height" -gt 2000 ]]; then
       printf "'$peer_ip:35000', "
     fi

  fi

}

function print_bad() {

  if ! [[ "$peer_height" =~ $numba ]]; then
    printf "$format" "$peer_ip"
  fi

}


dead_or_alive
