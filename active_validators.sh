#!/bin/bash

# Query active validators list, can accept input pub key: './active_validators.sh <validator_pub_key>' will output position and bond if active.

# Requirements: 'apt install jq'
# Requirements: Should run from active node with 'casper-client' available, used method 'get-auction-info'

# Known issue: On era change return bogus output ( ll ), still need to debug this, not yet sure if this is script related or API error.

LOCAL_HTTP_PORT='7777' # if any
API='127.0.0.1'

# -----------------------------------

IPv4_STRING='(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
NC='\033[0m'

if [[ "${#1}" -eq 64 ]]; then
   MyValidatorPubKey="$1"
elif [[ "${#1}" -eq 66 ]];then
   MyValidatorPubKey=$(echo "$1" | cut -c 3-)
else
   MyValidatorPubKey='false'
fi


echo && echo -e "${RED}If output show something like ${NC}<${GREEN}l ${CYAN}l${NC}>${RED}, run again in 2 minutes, will fix next update, known issue.${NC}" && echo

function GetCurrentEra() {

	read -r -a trustedHosts < <(echo $(cat /etc/casper/config.toml | grep 'known_addresses = ' | grep -E -o "$IPv4_STRING"))

	for seed_ip in "${trustedHosts[@]}"; do

		Ch_hash=$(curl -s --connect-timeout 3 --max-time 3 http://"$seed_ip":7777/status | jq -r '.last_added_block_info | .hash')

		if [[ "${#Ch_hash}" -eq 64 ]]; then
			era_current=$(curl -s http://"$seed_ip":7777/status | jq -r '.last_added_block_info | .era_id')
			era_return='true'
		fi

		if ! [[ "$era_current" =~ $numba ]]; then
			era_return='false'
		fi

	done
}

function QueryActiveValidatorsList() {

	ActiveValidatorsNow="0"

	COLUMNS=$(tput cols)
	divider=$(printf "%${COLUMNS}s" " " | tr " " "-")
	width=64

	auction_header="${CYAN}%42s\n${NC}"

	echo && printf "%$width.${width}s" "$divider"
	echo && printf "$auction_header" "VALIDATOR PUBLIC KEY"
	printf "%$width.${width}s\n" "$divider"

	numba='^[0-9]+$'

	ActiveValidatorsList=$(casper-client get-auction-info --node-address http://"$API":7777 | jq -r '.result | .era_validators.'\"$era_current\"'' | grep -v "{" | grep -v "}" | cut -c4- | tr -d ':",')

	ValidatrsListSorted=$(echo "$ActiveValidatorsList" | sort -nr -t" " -k2n | tac)

	while read validator; do
	
                Xbond_amount=$(echo -e "$validator" | cut -d ' ' -f 2)
                XValidator_pub_key=$(echo -e "$validator" | cut -d ' ' -f 1)

                KeyColor='\033[0;32m'
                BondColor='\033[0;33m'

                if [[ "$MyValidatorPubKey" =~ $XValidator_pub_key ]]; then

                        MyValidatorBidAmount="$Xbond_amount"
                        MyValidatorPosition="$ActiveValidatorsNow"
                        MyValidatorStatus="true"

                        KeyColor='\e[5m'
                        BondColor='\033[0;33m'

                fi

                echo -e "$KeyColor$XValidator_pub_key $BondColor$Xbond_amount${NC}"

                ActiveValidatorsNow=$((ActiveValidatorsNow+1))

	done <<<"$ValidatrsListSorted"

	printf "%$width.${width}s" "$divider"

	echo && echo -e "${GREEN}Active bonds: ${CYAN}$ActiveValidatorsNow ${GREEN}Active era: ${CYAN}$era_current${NC}"

	printf "%$width.${width}s" "$divider" && echo -e "\\n"

}

function ValidatorsConditionCheck() {

	if ! [[ "$MyValidatorPubKey" =~ false ]] && [[ "$MyValidatorStatus" =~ true ]]; then
		echo -e "Key is in ${GREEN}active${NC} bonds list, ${CYAN}$MyValidatorPosition${GREEN}, bond amount ${CYAN}$MyValidatorBidAmount${NC}" && echo
	elif ! [[ "$MyValidatorPubKey" =~ false ]] && ! [[ "$MyValidatorStatus" =~ true ]]; then
		echo -e "${RED}Public key is not present in active bonds.${NC}" && echo
		echo -e "${RED}Current minimum bid amount should be greater then: ${CYAN}$Xbond_amount${NC}" && echo
	fi

}

GetCurrentEra

if [[ "$era_return" =~ true ]]; then

	QueryActiveValidatorsList && ValidatorsConditionCheck

else

	echo -e "${RED}Can't get current era from trusted sources.${NC}" && echo && exit 1

fi
