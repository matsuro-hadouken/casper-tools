#!/bin/bash

# Copyright (C) 2020 Matsuro Hadouken <halfordico@protonmail.com>

# This file is free software; as a special exception the author gives
# unlimited permission to copy and/or distribute it, with or without
# modifications, as long as this notice is preserved.

# PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND

# --- SETUP ----------

DATA='/home/casper/.casperlabs'
GENESIS='/home/casper/.casperlabs/chainspec/genesis'

# --- END OF SETUP ---


Dispal_PID=$(pgrep casperlabs-engi)

clear

function StopService {

number='^[0-9]+$'

        if ! [[ $ENGI_PID =~ $number ]] ; then

		echo -e ''
		echo -e "\e[32mEngine is not active, nothing to destroy or break.\e[0m"
		echo -e ''

        else

		echo -e ''
		echo -e 'Shooting down CasperLabs Engine GRPC Server ...'
		echo -e ''
		echo -e "Process PID: $Dispal_PID"
		echo -e ''

		sleep 1

        		until [ $(systemctl is-active casperlabs-engine-grpc-server.service) = "inactive" ]

                		do
                        		systemctl stop casperlabs-engine-grpc-server.service & PID=$!

                        		wait $PID
                		done

		sleep 2
		echo -e '*DONE*'
		echo -e ''
		sleep 2
        fi
}


function CheckService {

echo -e 'Checking if service down one more time, just in case ...'
echo -e ''

ENGI_PID=$(pgrep casperlabs-engi)

number='^[0-9]+$'

	if [[ $ENGI_PID =~ $number ]] ; then
   		echo -e "\e[31merror: CasperLabs Engine GRPC Server is still running!\e[0m" >&2; exit 1
	else
		echo -e 'Check pass OK'
		echo -e ''
		sleep 1
	fi
}


function update {

echo -e 'Updating manifest.toml and accounts.csv'
echo ''

sleep 1

oldManifest=$(md5sum $GENESIS/manifest.toml)
oldAccounts=$(md5sum $GENESIS/accounts.csv)

echo -e 'Removing old files ...'
echo -e ''
echo -e 'Compare check sum ...'

sleep 1

echo -e ''
echo -e "\e[31mOld mnifest md5sum:\e[0m  $oldManifest"
echo -e "\e[31mOld accounts md5sum:\e[0m $oldAccounts"
echo -e ''

cd $DATA && rm -r sql* log* .casper-node.sock global_state > /dev/null 2>&1

cd $GENESIS && curl -O https://repo.casperlabs.io/casperlabs/repo/testing/manifest.toml > /dev/null 2>&1
cd $GENESIS && curl -O https://repo.casperlabs.io/casperlabs/repo/testing/accounts.csv  > /dev/null 2>&1

newManifest=$(md5sum $GENESIS/manifest.toml)
newAccounts=$(md5sum $GENESIS/accounts.csv)

echo -e "\e[32mNEW mnifest md5sum:\e[0m  $newManifest"
echo -e "\e[32mNEW accounts md5sum:\e[0m $newAccounts"
echo -e ''

}

function ListFoldersContent {

echo -e 'DATA folder content:'
echo -e ''

ls -la $DATA

echo -e ''
echo -e 'GENESIS folder content:'
echo -e ''

ls -la $GENESIS

}

StopService
CheckService
update
ListFoldersContent

echo -e ''
echo -e 'Everything should be ready to go.'
echo -e ''
echo -e 'Copy Paste for lazy people like me:' '\e[32msystemctl start casperlabs-engine-grpc-server.service\e[0m'
echo -e ''
