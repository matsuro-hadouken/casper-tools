#!/bin/bash

query_port='8888'
query_ip='<TRUSTED_SOURCE_IP>'
TrustedSource="http://$query_ip:$query_port/status"
config_path='/etc/casper/config.toml'
service_name='casperlabs'

database_location='/home/casper/.casperlabs/'
log_path='/home/casper/logs/'

function ClearLogs() {

    truncate -s 0 "$log_path"

}

function StopService() {

    unit_status="$(systemctl is-active $service_name | tr -d ' ')"

    if [ "$unit_status" = active ]; then

        echo "Service $service_name is $unit_status, safely terminating ..." && echo

        while [ "$unit_status" = active ]; do

            systemctl stop "$service_name"

            sleep 1

            unit_status="$(systemctl is-active $service_name | tr -d ' ')"

        done

    else

        echo "Service $service_name is $unit_status and does not require termination." && echo

    fi

}

function StartService() {

    echo "Starting service ..." && echo

    systemctl restart "$service_name"

}

function main() {

    StopService

    ClearDatabase

    TrustedHash

    echo "Looking for hash in config.toml ..." && sleep 1

    cat "$config_path" | grep 'trusted_hash = ' && echo

    CheckContent

    StartService

    echo "Service $service_name is $(systemctl is-active $service_name), mission complete." && echo

}

function CheckContent() {

    if [ ! "$(ls -A $database_location)" ]; then

        echo "ERROR: Database folder is not empty !" && echo && echo '-----' && echo

        ls -lah "$database_location" && echo '-----' && echo && exit 1

    else

        echo "Database clear, continue ..." && echo

    fi

}

function ClearDatabase() {

    double_check="$(systemctl is-active $service_name)"

    if [ "$double_check" = active ]; then

        echo "ERROR: Service $service_name is $double_check, we can't remove database, exit ..." && exit 1

    fi

    rm -rf "$database_location"*

}

function TrustedHash() {

    trusted_hash="$(curl -s --connect-timeout 2 --max-time 2 "http://$query_ip:$query_port/status" | jq -r '.last_added_block_info | .hash')"

    if ! [[ "${#trusted_hash}" -eq 64 ]]; then

        echo "Query failed, trusted source replay: $trusted_hash" && echo && exit 1

    fi

    echo "Adding hash $trusted_hash in to $config_path ..." && echo

    sed -i '10s/.*/trusted_hash = '"'$trusted_hash'"'/' "$config_path"

}

function WatchDog() {

    echo "Printing content of the error log ..." && echo '==============================================================================' && echo

    cat "$log_path*.err"

    echo "Tailing logstream, Ctrl +C to stop ..." && sleep 1 && echo

    tail -f "$log_path*.log" | jq

}

echo && main

ClearLogs

WatchDog
