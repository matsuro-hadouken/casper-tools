#!/bin/bash

query_port='8888'
query_ip='54.183.27.7'
TrustedSource="http://$query_ip:$query_port/status"
config_path='/etc/casper/config.toml'
service_name='casperlabs'
database_location='/home/casper/.casperlabs/'

# ===========================================

function main() {

    unit_status="$(systemctl is-active $service_name)"

    if [[ "$unit_status" =~ active ]]; then

        echo "Service $service_name is active, safely terminating ..." && echo
        systemctl stop "$service_name"
        sleep 5
    fi

    ClearDatabase

    TrustedHash

    cat "$config_path" | grep 'trusted_hash = ' && echo

    echo "Content of the database folder:" && echo

    ls "$database_location" && echo

    systemctl restart "$service_name"

    echo "Service $service_name is $(systemctl is-active $service_name)" && echo
}

function ClearDatabase() {

    unit_status="$(systemctl is-active $service_name)"

    if [[ "$unit_status" =~ active ]]; then
        echo "Service $service_name is active, we can't remove database, exit ..." && exit 1
    fi

    rm -rf "$database_location"*

}

function TrustedHash() {

    trusted_hash="$(curl -s --connect-timeout 2 --max-time 2 http://54.183.27.75:8888/status | jq -r '.last_added_block_info | .hash')"

    if ! [[ "${#trusted_hash}" -eq 64 ]]; then

        echo && echo "Query failed, trusted source replay: $trusted_hash" && echo && exit 1

    fi

    echo "Adding hash $trusted_hash in to $config_path ..." && echo

    sed -i '10s/.*/trusted_hash = '"'$trusted_hash'"'/' "$config_path"

}

main
