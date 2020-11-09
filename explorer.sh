#!/bin/bash

# Works with 'Delta-1'

# Matsuro Hadouken <matsuro-hadouken@protonmail.com> 2020

# This file is free software; as a special exception the author gives
# unlimited permission to copy and/or distribute it, with or without
# modifications, as long as this notice is preserved.

# PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND

LOCAL_HTTP_PORT='7777'       # if any
HostLocalNetwork='127.0.0.1' # if any

IPv4_STRING='(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ValidatorsCount="0"
UselessHosts="0"
BlockedHTTP="0"
AvailableHosts="0"

header="${CYAN} %-10s %-16s %10s %20s %9s %7s %11s\n${NC}"

COLUMNS=$(tput cols)
divider=$(printf "%${COLUMNS}s" " " | tr " " "-")
width=92

function Report() {

    NC='\033[0m'

    color=$(echo "$@" | cut -d" " -f1)
    msg=$(echo "$*" | cut -d" " -f2-)

    [[ $color == WHITE ]] && color="$WHITE"
    [[ $color == RED ]] && color="$RED"
    [[ $color == GREEN ]] && color="$GREEN"
    [[ $color == CYAN ]] && color="$CYAN"

    echo -e "$color$msg${NC}" && echo
} # useless for the moment

function Seeds() {

    declare -a TrustedHashArray

    echo && printf "$header" "STATUS" "IP ADDRESS" "TRUSTED HASH" "CHAIN NAME" "ERA" "HEIGH" "VERSION"

    printf "%$width.${width}s\n" "$divider"

    read -r -a trustedHosts < <(echo $(cat /etc/casper/config.toml | grep 'known_addresses = ' | grep -E -o "$IPv4_STRING"))

    for seed_ip in "${trustedHosts[@]}"; do

        GetPeerData "$seed_ip"

        TrustedHashArray+=("$LastAddedBlockHash")

        printf "$format" "$HostStatus" "$seed_ip" "$last_added_block_hash" "$chainspec_name" "$era_id" "$chain_height" "$build_version"

    done

    printf "%$width.${width}s\n" "$divider"

    if ! [[ "${TrustedHashArray[0]}" =~ ${TrustedHashArray[1]} ]] && ! [[ "${TrustedHashArray[1]}" =~ ${TrustedHashArray[2]} ]]; then

        Report RED "Trusted validators hash missmatch, please run script again." && exit

    else

        ReferenceChainspec=$chainspec_name
        ReferenceBuildVersion=$build_version
        ReferenceIP=$seed_ip
        TrustedHash=$LastAddedBlockHash

    fi

}

function Condition() {

    if [[ "${#LastAddedBlockHash}" -eq 64 ]] && [[ ! "$LastAddedBlockHash" =~ 'null' ]]; then
        format=" ${GREEN}%-10s${NC} %-16s %17s %19s %5s %6s %10s\n"
        HostStatus='Trusted'
    elif [[ "$LastAddedBlockHash" =~ 'null' ]]; then
        format=" ${CYAN}%-10s${NC} %-16s %17s %19s %5s %6s %10s\n"
        HostStatus='Genesis'
    else
        format=" ${RED}%-10s${NC} %-16s %17s %19s %5s %6s %10s\n"
        HostStatus='Bogus'
    fi
}

function GetPeerData() {

    validator_ip="$1"

    Stage="$2"

    PeerDataList=$(curl -s --connect-timeout 2 --max-time 2 http://$validator_ip:7777/status | jq -r '.build_version, .chainspec_name, .last_added_block_info.hash, .last_added_block_info.era_id, .last_added_block_info.height')

    if ! [[ $PeerDataList ]]; then

        format=" ${YELLOW}%-10s %-16s %17s %19s %5s %6s %10s${NC}\n"

        HostStatus='Blocked'

        build_version=''
        chainspec_name=''
        last_added_block_hash=''
        era_id=''
        chain_height=''

        BlockedHTTP=$((BlockedHTTP + 1))

        return

    fi # NO HTTP ACCESS OR DEAD PEER

    readarray -t PeerDataArray <<<"$PeerDataList"

    LastAddedBlockHash=${PeerDataArray[2]}

    build_version=${PeerDataArray[0]}
    chainspec_name=${PeerDataArray[1]}

    if [[ $LastAddedBlockHash == "null" ]]; then
        last_added_block_hash="null"
    else
        last_added_block_hash="$(echo "$LastAddedBlockHash" | cut -c1-5) .... $(echo "$LastAddedBlockHash" | cut -c59-64)"
    fi

    era_id=${PeerDataArray[3]}
    chain_height=${PeerDataArray[4]}

    if [[ "$Stage" =~ "COUNT" ]]; then
        ValidatorsCount=$((ValidatorsCount + 1))
    else
        Condition
    fi

}

function CheckPeers() {

    read -r -a peers_list < <(echo $(curl -s http://127.0.0.1:7777/status | jq .peers | grep -E -o "$IPv4_STRING"))

    for peer_ip in "${peers_list[@]}"; do

        format=" %-10s %-16s %17s %19s %5s %6s %10s\n"

        HostStatus='Available'

        GetPeerData "$peer_ip" "COUNT"

        if ! [[ $HostStatus =~ 'Blocked' ]] && ! [[ $chainspec_name =~ $ReferenceChainspec ]]; then
            format=" ${RED}%-10s %-16s %-17s %19s %5s %6s %10s${NC}\n"
            HostStatus='Useless'
            UselessHosts=$((UselessHosts + 1))
        elif ! [[ $HostStatus =~ 'Blocked' ]] && [[ $chainspec_name =~ $ReferenceChainspec ]]; then
            AvailableHosts=$((AvailableHosts + 1))
        fi

        #    0            1              2              3          4        5         6
        # "STATUS"  "IP ADDRESS"  "TRUSTED HASH"  "CHAIN NAME"   "ERA"   "HEIGH"  "VERSION"

        printf "$format" "$HostStatus" "$peer_ip" "$last_added_block_hash" "$chainspec_name" "$era_id" "$chain_height" "$build_version"

    done
}

function CheckActiveHost() {

    # check if run from active active validator host, so it will be +1
    if [[ $(curl -s http://$HostLocalNetwork:"$LOCAL_HTTP_PORT"/status | jq -r .api_version) ]]; then

        GetPeerData "$HostLocalNetwork" "COUNT"
        HostStatus='HOST'
        peer_ip=$HostLocalNetwork

        if [[ $chainspec_name =~ $ReferenceChainspec ]]; then
            format=" ${BLUE}%-10s${NC} %-16s %-17s %19s %5s %6s %10s${NC}\n"
            AvailableHosts=$((AvailableHosts + 1))
        else
            format=" ${RED}%-10s${NC} %-16s ${RED}%-17s${NC} %19s %5s %6s %10s${NC}\n"
            UselessHosts=$((UselessHosts + 1)) # THIS NEED TO REWRITE WITH CHECK FOR OUTSIDE PORT ACCESS ( BLOCKED / AWAILABLE )
        fi
    fi

    printf "$format" "$HostStatus" "$peer_ip" "$last_added_block_hash" "$chainspec_name" "$era_id" "$chain_height" "$build_version"
}

Seeds

CheckActiveHost

CheckPeers

echo && echo -e "${CYAN}Trusted hash:${NC} ${GREEN}$TrustedHash${NC}" && echo

echo "PeersCount:     $ValidatorsCount" && echo

echo "Useless peers:  $UselessHosts"
echo "Blocked access: $BlockedHTTP"
echo "Good condition: $((ValidatorsCount - UselessHosts - BlockedHTTP))" && echo

# echo "Good condition: $AvailableHosts" && echo # Work in progress
