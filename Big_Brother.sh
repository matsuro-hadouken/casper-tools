#!/bin/bash

# primitive network crawler for debugging
# I run this as systemd service

INITIAL_IP='127.0.0.1'
STATUS_PORT='8888'

# tmp base.1
base_1='/home/casper/casper-tools/crawler/base.1'
# tmp base 2
base_2='/home/casper/casper-tools/crawler/base.2'
# main collector which never got truncated
big_brother='/home/casper/casper-tools/crawler/big.brother'

function start_init() {

  curl -s --max-time 10 --connect-timeout 10 http://"$INITIAL_IP":"$STATUS_PORT"/status | jq -r '.peers | .[].address' | cut -f1 -d":" > "$base_1"

  crawler

}

function crawler() {

  while IFS= read -r peer_ip; do

    curl -s --max-time 10 --connect-timeout 10 http://"$peer_ip":"$STATUS_PORT"/status | jq -r '.peers | .[].address' | cut -f1 -d":" >>"$base_2"

  done <"$base_1"

  sort_u

}

function sort_u() {

  sort -u "$base_2" -o "$base_2"

  cat "$base_2" >"$base_1"
  cat "$base_2" >>"$big_brother"

  sort -u "$big_brother" -o "$big_brother"

  # debiug :=D
  # clear && cat "$base_1"

  crawler

}

start_init
