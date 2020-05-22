#!/bin/bash

DATA='/home/casper/.casperlabs'
GENESIS='/home/casper/.casperlabs/chainspec/genesis'

Dispal_PID=$(pgrep casperlabs-engi)

clear

function StopService() {

    number='^[0-9]+$'

    if ! [[ $ENGI_PID =~ $number ]]; then # check if service active

        echo && echo -e "\e[32mEngine is not active, nothing to destroy or break.\e[0m" && echo

    else # if active safely shutdown

        echo && echo 'Shooting down CasperLabs Engine GRPC Server ...' && echo
        echo "Process PID: $Dispal_PID" && echo

        sleep 1

        until [ $(systemctl is-active casperlabs-engine-grpc-server.service) = "active" ]; do

            systemctl stop casperlabs-engine-grpc-server.service &

            PID=$!

            wait $PID

            sleep 5

        done

        echo -e '*DONE*' && echo && sleep 3

    fi
}

function CheckService() {

    echo 'Checking if service down one more time, just in case ...' && echo

    ENGI_PID=$(pgrep casperlabs-engi)

    number='^[0-9]+$'

    while [[ $ENGI_PID =~ $number ]]; do

        echo -e "\e[31merror: CasperLabs Engine GRPC Server is still running!\e[0m" && echo
        echo -e "\e[31mKilling $ENGI_PID PID ...\e[0m" && echo

        kill -9 $ENGI_PID && PID=$! >/dev/null 2>&1

        wait $PID

        ENGI_PID=$(pgrep casperlabs-engi)

        sleep 1

    done

    echo -e 'Check pass OK' && echo && sleep 1
}

function update() {

    sudo apt update && sudo apt upgrade -y

    echo && echo "Server upgrade complete." && echo && sleep 5

    echo 'Updating manifest.toml and accounts.csv' && echo

    sleep 1

    oldManifest=$(md5sum $GENESIS/manifest.toml)
    oldAccounts=$(md5sum $GENESIS/accounts.csv)

    echo 'Removing old files ...' && echo && echo 'Compare check sum ...'

    sleep 1

    echo && echo -e "\e[31mOld mnifest md5sum:\e[0m  $oldManifest"
    echo -e "\e[31mOld accounts md5sum:\e[0m $oldAccounts" && echo

    cd $DATA && rm -r sql* log* .casper-node.sock global_state >/dev/null 2>&1

    echo && echo 'Truncate EE log ...' && echo && sleep 2

    sudo sudo truncate -s 0 /var/log/casperlabs-node.log

    echo

    cd $GENESIS && curl -O https://raw.githubusercontent.com/CasperLabs/CasperLabs/dev/testnet/accounts.csv >/dev/null 2>&1
    cd $GENESIS && curl -O https://raw.githubusercontent.com/CasperLabs/CasperLabs/dev/testnet/manifest.toml >/dev/null 2>&1

    newManifest=$(md5sum $GENESIS/manifest.toml)
    newAccounts=$(md5sum $GENESIS/accounts.csv)

    echo -e "\e[32mNEW mnifest md5sum:\e[0m  $newManifest"
    echo -e "\e[32mNEW accounts md5sum:\e[0m $newAccounts" && echo

}

function ListFoldersContent() {

    echo 'DATA folder content:' && echo

    ls -la $DATA

    echo && echo 'GENESIS folder content:' && echo

    ls -la $GENESIS

}

StopService
CheckService
update
ListFoldersContent

echo
casperlabs-engine-grpc-server --version
echo
casperlabs-node --version

echo
echo 'Everything should be ready to go.'
echo
echo -e 'Copy Paste for lazy people like me:' '\e[32msudo systemctl start casperlabs-engine-grpc-server.service\e[0m'
echo
