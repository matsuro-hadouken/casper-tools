#!/bin/bash

# Query active validators list, can accept input pub key: './active_validators.sh <validator_pub_key>' will output position and bond if active.
# If no input provided will check '$public_hex_path' path for 'public_key_hex'

# Requirements: 'apt install jq'
# Requirements: 'apt install bc'

# Requirements: Should run from active node with 'casper-client' available, used method 'get-auction-info'

public_hex_path='/etc/casper/validator_keys/public_key_hex'

trusted_cap="3"		# how many trusted IP we validate, since is to many of them in config now.
show_decimals="0"	# CSPR decimals ( 0 = no decimals )

HTTP_PORT="8888"
RPC_PORT="7777"
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
        echo -e " ${RED}No valid manual input detected !${NC}" && echo
        echo -e " Using public HEX from: ${RED}$public_hex_path${NC}"

    else

        MyValidatorPubKey='false'

    fi

    echo && echo -e " Public HEX: ${CYAN}$MyValidatorPubKey${NC}"

}

function CreateTemporaryFolder() {

    chain_name="-$(curl -s http://$API:$HTTP_PORT/status | jq -r .chainspec_name)"

    TMPDIR=$(mktemp -d --suffix="$chain_name")

    if [ ! -e "$TMPDIR" ]; then

        echo >&2 -e " ${RED}Failed to create temp directory${NC}" && echo
        exit 1

    fi

    trap "exit 1" HUP INT PIPE QUIT TERM
    trap 'rm -rf "$TMPDIR"' EXIT

}

function GetCurrentEra() {

    trusted_ip_era_arr=()

    trusted_counter=0

    active_config=$(ps -ef | grep casper | grep config.toml | head -1 | awk -F" " '{print $10}')

    if [[ "${#active_config}" -lt 3 ]]; then
      echo && echo -e " ${RED}ERROR:${NC} Can't get active configuration version from localhost, we need trusted endpoints from ${GREEN}/etc/casper/${RED}<version>${GREEN}/config.toml${NC}, terminating ..." && echo && sleep 1 && exit
    fi

    host_era_current=$(curl -s --connect-timeout 3 --max-time 3 "http://localhost:$HTTP_PORT/status" | jq -r '.last_added_block_info | .era_id')

    if ! [[ "$host_era_current" =~ $numba ]]; then
      echo && echo -e " ${RED}Can't get era from host !${NC} Replay: [ $host_era_current ]"
    fi

    echo && echo -e " We believe active host config version: ${GREEN}$active_config${NC}, host era: ${GREEN}$host_era_current${NC}"

    read -r -a trustedHosts < <(echo $(cat $active_config | grep 'known_addresses = ' | grep -E -o "$IPv4_STRING"))

    for seed_ip in "${trustedHosts[@]}"; do

        Ch_hash=$(curl -s --connect-timeout 3 --max-time 3 "http://$seed_ip:$HTTP_PORT"/status | jq -r '.last_added_block_info | .hash')

        trusted_counter=$(( trusted_counter + 1 ))

        if [[ "${#Ch_hash}" -eq 64 ]]; then

            era_current=$(curl -s "http://$seed_ip:$HTTP_PORT/status" | jq -r '.last_added_block_info | .era_id')
            echo && echo -e " Trusted host: ${GREEN}$seed_ip${NC}, era: ${GREEN}$era_current${NC}, hash: ${GREEN}$Ch_hash${NC}"

            trusted_ip_era_arr=( "${trusted_ip_era_arr[@]}" "$era_current" )

        fi

        if ! [[ "$era_current" =~ $numba ]]; then
            echo && echo -e " ${YELLOW}INFO:${NC} Can't get data from ${GREEN}$seed_ip${NC}, blocked or inactive, skip ..."
        fi

        if ! [ "$era_current" != $numba ] && [ "$trusted_counter" -ge $trusted_cap ]; then
            echo -e " ${RED}ERROR:${NC} Can't get era from trusted array, terminating ..." && sleep 1 && exit
        fi

        if [[ "$trusted_counter" -ge $trusted_cap ]]; then
                break
        fi

    done

    if ! [[ "$era_current" =~ $numba ]]; then

      echo && echo -e " ${RED}ERROR:${NC} Not able to get current era from trusted hosts, terminating ..." && echo && sleep 1 && exit

    fi

    for era in "${trusted_ip_era_arr[@]}" ; do ((era > chain_top_era)) && chain_top_era=$era; done

    era_current="$chain_top_era"

    echo && echo -e " ${CYAN}Current era: ${GREEN}$era_current${NC}" && echo

}

function GetVisibleEras() {

    IFS=$'\n' VisibleEras=($(casper-client get-auction-info | jq -r '.result.auction_state.era_validators | .[] | .era_id'))

}

function BrowseTroughEras() {

    echo && echo ' ------------------------------------------------------------------'
    echo -e " ${CYAN}Ongoing era: ${YELLOW}$era_current${CYAN}, looking in to future ...      Following sequence: ${YELLOW}${VisibleEras[@]}${NC}"
    echo ' ------------------------------------------------------------------'

    era_section=$(casper-client get-auction-info | jq -r '.result.auction_state.era_validators | .[]')

    for era in "${VisibleEras[@]}"; do

	validator_era=$(echo $era_section | jq -r 'select(.era_id=='$era')')
        validators_in_era=$(echo $validator_era | jq -r '.validator_weights | length')

        echo && echo -e " >>> ${YELLOW}Crawling era: ${CYAN}$era${YELLOW} amount of bonds: ${CYAN}$validators_in_era${NC}" && echo

        for ((i = 0; i < "$validators_in_era"; ++i)); do
			echo $validator_era | jq -r '.validator_weights['$i'] | [.public_key,.weight] | join(" ")'

        done >"$TMPDIR/$era.db"

        cat "$TMPDIR/$era.db" | sort -nr -t" " -k2n | tac >tmp && mv tmp "$TMPDIR/$era.db"

        PrittyPrint "$TMPDIR/$era.db"

    done
}

function PrittyPrint() {

    ActiveValidatorsNow="1"

    while IFS= read -r validator; do

        XValidator_pub_key=$(echo -e $validator | cut -d ' ' -f 1)
        Xbond_amount=$(echo "scale=$show_decimals; $(echo -e $validator | cut -d ' ' -f 2) / 1000000000" | bc -l)

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
        echo -e " $KeyColor$XValidator_pub_key $BondColor$Xbond_amount${NC}"

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

    echo -e " ${YELLOW}>>>>>>>>> ${CYAN}ERA $era${NC}" >>"$TMPDIR/report.txt"

    if [[ "$MyValidatorStatus" =~ true ]]; then

        echo -e " Key is in ${GREEN}active${NC} validators list !" >>"$TMPDIR/report.txt"
        echo -e " Position ${GREEN}$MyValidatorPosition${NC}, validator weight: ${YELLOW}$MyValidatorBidAmount${NC}" >>"$TMPDIR/report.txt"
        echo -e " Active bonds: ${GREEN}$(($ActiveValidatorsNow - 1))${NC}" >>"$TMPDIR/report.txt"
        echo >> "$TMPDIR/report.txt"

    elif ! [[ "$MyValidatorPubKey" =~ false ]] && ! [[ "$MyValidatorStatus" =~ true ]]; then

        echo -e " Key is ${RED}not${NC} in active validators list !" >>"$TMPDIR/report.txt"
        echo -e " Era minimum bid should be greater then: ${YELLOW}$Xbond_amount${NC}" >>"$TMPDIR/report.txt"
        echo -e " Active bonds: ${GREEN}$(($ActiveValidatorsNow - 1))${NC}" >>"$TMPDIR/report.txt"
        echo >> "$TMPDIR/report.txt"

    fi
}

function CheckAuction() {

    total_bids="0"
    Is_validator_in_bid_list="false"

    echo && echo ' ------------------------------------------------------------------'
    echo -e " ${YELLOW}Crawling trough auction order book, looking for public key ...${NC}"
    echo ' ------------------------------------------------------------------' && echo && sleep 1

    # collect auction data >tmp
    casper-client get-auction-info --node-address "http://$API:$RPC_PORT" >"$TMPDIR/tmp.auction"

    bids=$(cat "$TMPDIR/tmp.auction" | jq '.result.auction_state.bids')
    ace_of_base=$(echo $bids | jq 'length')

    for ((b = 0; b < "$ace_of_base"; ++b)); do
	echo $bids | jq -r '.['$b'] | [.public_key,.bid.staked_amount,.bid.reward] |join(" ")'
        total_bids=$((total_bids + 1))

    done >"$TMPDIR/tmp.bids"

    # rearrange bids by value
    cat "$TMPDIR/tmp.bids" | sort -nr -t" " -k2n | tac >tmp && mv tmp "$TMPDIR/tmp.bids"

    val_count="1"

    # crawling trough already sorted list
    while read line; do

        KeyColor='\e[0;35m'
        BondColor='\033[0;33m'

        bid_pub_key=$(echo "$line" | cut -d ' ' -f 1)
        bid_amount=$(echo "scale=$show_decimals; $(echo "$line" | cut -d ' ' -f 2) / 1000000000" | bc -l)

        # if key present in bid list
        if [[ "$MyValidatorPubKey" =~ $bid_pub_key ]]; then

            validator_bid_list_amount="$bid_amount"
            Is_validator_in_bid_list="true"

            KeyColor='\e[5m'
            BondColor='\033[0;33m'

            validator_position_In_BidList="$val_count"

        fi

        echo -e " $KeyColor$bid_pub_key $BondColor$bid_amount${NC}"

        val_count=$((val_count + 1))

    done <"$TMPDIR/tmp.bids"

    if ! [[ "$Is_validator_in_bid_list" =~ false ]]; then

        echo -e " ${CYAN}Bid ${GREEN}registered${NC}${CYAN}, position ${GREEN}$validator_position_In_BidList${CYAN}, bid amount: ${YELLOW}$validator_bid_list_amount${NC}" >>"$TMPDIR/report.txt"

    else

        echo -e " This public key ${RED}is not${NC} in auction." >>"$TMPDIR/report.txt"

    fi

    echo >> "$TMPDIR/report.txt"
    echo -e " ${CYAN}Total bids made in to acution house: ${GREEN}$total_bids${NC}" >>"$TMPDIR/report.txt"
    echo >> "$TMPDIR/report.txt"

    auction_best_bid=$(echo "scale=$show_decimals; $(cat $TMPDIR/tmp.bids | head -n1 | cut -d ' ' -f 2) / 1000000000" | bc -l)
    auction_bottom_b=$(echo "scale=$show_decimals; $(cat $TMPDIR/tmp.bids | tail -n1 | cut -d ' ' -f 2) / 1000000000" | bc -l)

    echo -e " ${CYAN}Best bid:${NC}   $auction_best_bid" >>"$TMPDIR/report.txt"
    echo -e " ${CYAN}Bottom bid:${NC} $auction_bottom_b" >>"$TMPDIR/report.txt"
    echo >> "$TMPDIR/report.txt"

}

GetCurrentEra

GetPublicHEX "$1"

CreateTemporaryFolder

GetVisibleEras

BrowseTroughEras

CheckAuction

echo && cat "$TMPDIR/report.txt"
