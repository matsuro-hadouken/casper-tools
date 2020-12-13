#!/bin/bash

# Query active validators list, can accept input pub key: './active_validators.sh <validator_pub_key>' will output position and bond if active.

# Requirements: 'apt install jq'
# Requirements: Should run from active node with 'casper-client' available, used method 'get-auction-info'

public_hex_path='/etc/casper/validator_keys/public_key_hex'

HTTP_PORT="8888"
API='127.0.0.1'

IPv4_STRING='(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
NC='\033[0m'

numba='^[0-9]+$'

function GetPublicHEX() {

    manual_input="$1"

    AutoHEX=$(cat "$public_hex_path")

    if [[ "${#manual_input}" -eq 66 ]]; then

        MyValidatorPubKey="$1"

    elif [[ "${#AutoHEX}" -eq 66 ]]; then

        MyValidatorPubKey="$AutoHEX"
        echo && echo -e "${RED}No valid manual input detected !${NC}" && echo
        echo -e "Using public HEX from: ${RED}$public_hex_path${NC}"

    else

        MyValidatorPubKey='false'

    fi

    echo && echo -e "Public HEX: ${CYAN}$MyValidatorPubKey${NC}"

}

function CreateTemporaryFolder() {

    chain_name="-$(curl -s http://$API:$HTTP_PORT/status | jq -r .chainspec_name)"

    TMPDIR=$(mktemp -d --suffix="$chain_name")

    if [ ! -e "$TMPDIR" ]; then

        echo >&2 -e "${RED}Failed to create temp directory${NC}" && echo
        exit 1

    fi

    trap "exit 1" HUP INT PIPE QUIT TERM
    trap 'rm -rf "$TMPDIR"' EXIT

}

function GetCurrentEra() {

    read -r -a trustedHosts < <(echo $(cat /etc/casper/config.toml | grep 'known_addresses = ' | grep -E -o "$IPv4_STRING"))

    for seed_ip in "${trustedHosts[@]}"; do

        echo && echo -e "Trusted address list: ${GREEN}$seed_ip${NC}, query era ..."

        Ch_hash=$(curl -s --connect-timeout 3 --max-time 3 "http://$seed_ip:$HTTP_PORT"/status | jq -r '.last_added_block_info | .hash')

        if [[ "${#Ch_hash}" -eq 64 ]]; then
            era_current=$(curl -s "http://$seed_ip:$HTTP_PORT/status" | jq -r '.last_added_block_info | .era_id')
        fi

        if ! [[ "$era_current" =~ $numba ]]; then
            echo -e "${RED}ERROR: Bogus output [ $era_current ] from ${GREEN}$seed_ip${RED}, exit ...${NC}" && echo && exit 1
        fi

    done
}

function GetVisibleEras() {

    IFS=$'\n' VisibleEras=($(casper-client get-auction-info | jq -r '.result | .era_validators | .[] | .era_id'))

}

function DrawLine() {

    echo && echo "------------------------------------------------------------------" && echo

}

function BrowseTroughEras() {

    echo && echo -e "${CYAN}Ongoing era: ${YELLOW}$era_current${CYAN}, looking in to future ... following sequence: ${YELLOW}${VisibleEras[@]}${NC}"

    for era in "${VisibleEras[@]}"; do

        validators_in_era=$(casper-client get-auction-info | jq -r '.result | .era_validators | .[] | select(.era_id=='$era') | .validator_weights | length')

        echo && echo -e "---> ${YELLOW}Crawling era: ${CYAN}$era${YELLOW} amount of bonds: ${CYAN}$validators_in_era${NC}" && echo

        for ((i = 0; i < "$validators_in_era"; ++i)); do

            validator_bublic_key=$(casper-client get-auction-info | jq -r '.result | .era_validators | .[] | select(.era_id=='$era') | .validator_weights['$i'] | .public_key')
            validator_weight=$(casper-client get-auction-info | jq -r '.result | .era_validators | .[] | select(.era_id=='$era') | .validator_weights['$i'] | .weight')

            echo "$validator_bublic_key $validator_weight"

        done >"$TMPDIR/$era.db"

        cat "$TMPDIR/$era.db" | sort -nr -t" " -k2n | tac >tmp && mv tmp "$TMPDIR/$era.db"

        PrittyPrint "$TMPDIR/$era.db"

    done

}

function PrittyPrint() {

    ActiveValidatorsNow="1"

    while IFS= read -r validator; do

        XValidator_pub_key=$(echo -e "$validator" | cut -d ' ' -f 1)
        Xbond_amount=$(echo -e "$validator" | cut -d ' ' -f 2)

        KeyColor='\033[0;32m'
        BondColor='\033[0;33m'

        # if key is present in era
        if [[ "$MyValidatorPubKey" =~ $XValidator_pub_key ]]; then

            MyValidatorBidAmount="$Xbond_amount"
            MyValidatorPosition="$ActiveValidatorsNow"
            MyValidatorStatus="true"

            KeyColor='\e[5m'
            BondColor='\033[0;33m'

        fi

        # this will also set minimum bid amount, because we sort from height to low, last read will be the lowest one.
        echo -e "$KeyColor$XValidator_pub_key $BondColor$Xbond_amount${NC}"

        # count validators in era
        ActiveValidatorsNow=$((ActiveValidatorsNow + 1))

    done <"$1"

    # if we have public hex as input
    if ! [[ "$MyValidatorPubKey" =~ false ]]; then

        # send for report
        EraConditionReport

    fi

}

function EraConditionReport() {

    echo -e "${YELLOW}--------> ${CYAN}ERA $era${NC}" >>"$TMPDIR/report.txt"

    if [[ "$MyValidatorStatus" =~ true ]]; then

        echo -e "Key is in ${GREEN}active${NC} validator list !" >>"$TMPDIR/report.txt"
        echo -e "Position ${GREEN}$MyValidatorPosition${NC}, bond amount: ${YELLOW}$MyValidatorBidAmount${NC}" >>"$TMPDIR/report.txt"
        echo -e "Active bonds: ${GREEN}$(($ActiveValidatorsNow - 1))${NC}" >>"$TMPDIR/report.txt"
        echo >>"$TMPDIR/report.txt"

    elif ! [[ "$MyValidatorPubKey" =~ false ]] && ! [[ "$MyValidatorStatus" =~ true ]]; then

        echo -e "Key is ${RED}not${NC} in active bonds list !" >>"$TMPDIR/report.txt"
        echo -e "Era minimum bid should be greater then: ${YELLOW}$Xbond_amount${NC}" >>"$TMPDIR/report.txt"
        echo -e "Active bonds: ${GREEN}$(($ActiveValidatorsNow - 1))${NC}" >>"$TMPDIR/report.txt"
        echo >>"$TMPDIR/report.txt"

    fi
}

GetCurrentEra

GetPublicHEX "$1"

CreateTemporaryFolder

GetVisibleEras

BrowseTroughEras

echo && cat "$TMPDIR/report.txt"
