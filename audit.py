#!/usr/bin/python3
import sys,os,curses,json,time,select,random,threading,urllib.request,contextlib
from datetime import datetime,timedelta,timezone
from collections import namedtuple
from configparser import ConfigParser
import platform,subprocess,re,getopt
import requests,hmac,hashlib,base64
import math,calendar,csv

#-------------------------------------------------------
public_key = None
localhost = 'localhost'
output_file = None
#-------------------------------------------------------
start_day = None
start_month = None
start_year = None
#-------------------------------------------------------
last_day = None
last_month = None
last_year = None
#-------------------------------------------------------
num_decimals = 2
#-------------------------------------------------------

def checkBalance(block):
    while True:
        try:
            block_info = json.loads(os.popen('casper-client get-block -b {} --node-address https://rpc.mainnet.casperlabs.io/rpc'.format(block)).read())
            state_root = block_info['result']['block']['header']['state_root_hash']
            break
        except:
            pass
    
    while True:
        try:
            query_state = json.loads(os.popen('casper-client query-state -k {} -s {} --node-address https://rpc.mainnet.casperlabs.io/rpc'.format(public_key, state_root)).read())
            main_purse = query_state['result']['stored_value']['Account']['main_purse']
            break
        except:
            pass

    while True:
        try:
            balance_info = json.loads(os.popen('casper-client get-balance --purse-uref {} --state-root-hash {} --node-address https://rpc.mainnet.casperlabs.io/rpc'.format(main_purse, state_root)).read())
            balance = balance_info['result']['balance_value']
            break
        except:
            pass

    return int(balance)

#-------------------------------------------------------

def getAuctionInfo(block):
    while True:
        try:
            auction_info = json.loads(os.popen('casper-client get-auction-info -b {} --node-address https://rpc.mainnet.casperlabs.io/rpc'.format(block)).read())
            auction_info = auction_info['result']['auction_state']
            bid_info = auction_info['bids']
            break
        except:
            pass

    for item in bid_info:
        key = item['public_key'].strip("\"")
        value = int(item['bid']['staked_amount'].strip("\""))
        if key == public_key:
            return int(value)

    return 0

def run():

    while True:
        try:
            block_info = json.loads(os.popen('casper-client get-block --node-address https://rpc.mainnet.casperlabs.io/rpc').read())
            currentProposerBlock = int(block_info['result']['block']['header']['height'])
            event_time = datetime.strptime(block_info['result']['block']['header']['timestamp'],'%Y-%m-%dT%H:%M:%S.%fZ')
            break
        except:
            pass

    print('\nAll data is gathered at the beginning of each day, and then a final entry is on the last day @11:59pm\n(so you can see total earning from Midnight on first day to Midnight on last day)')
    print("\nCasper Blockchain is currently at Block:", currentProposerBlock)
    print("\nUsing Public Key", public_key)

    today = datetime.now(timezone.utc).date()
    first = today.replace(day=1)
    lastDayMonth = first - timedelta(days=1)
    firstDayMonth = lastDayMonth.replace(day=1)

    if event_time.date() > lastDayMonth:
        currentProposerBlock -= (event_time.day -1) * 5300

    if start_day != None:
        a,z = calendar.monthrange(firstDayMonth.year, firstDayMonth.month)
        firstDayMonth = firstDayMonth.replace(day=z if start_day > z else start_day)

    if start_month != None:
        a,z = calendar.monthrange(firstDayMonth.year, start_month)
        firstDayMonth = firstDayMonth.replace(day=z if firstDayMonth.day > z else firstDayMonth.day)
        firstDayMonth = firstDayMonth.replace(month=start_month)

    if start_year != None:
        a,z = calendar.monthrange(start_year, firstDayMonth.month)
        firstDayMonth = firstDayMonth.replace(day=z if firstDayMonth.day > z else firstDayMonth.day)
        firstDayMonth = firstDayMonth.replace(year=start_year)

    if last_day != None:
        a,z = calendar.monthrange(lastDayMonth.year, lastDayMonth.month)
        lastDayMonth = lastDayMonth.replace(day=z if last_day > z else last_day)

    if last_month != None:
        a,z = calendar.monthrange(lastDayMonth.year, last_month)
        lastDayMonth = lastDayMonth.replace(day=z)
        lastDayMonth = lastDayMonth.replace(month=last_month)

    if last_year != None:
        a,z = calendar.monthrange(last_year, lastDayMonth.month)
        lastDayMonth = lastDayMonth.replace(day=z)
        lastDayMonth = lastDayMonth.replace(year=last_year)

    print("\nGetting Info for", firstDayMonth, "to", lastDayMonth, "\n")

    lastDayBlock = 0
    firstDayBlock = 0
    retryMessage = ""
    blockAmount = 100
    while currentProposerBlock >= 0 and firstDayBlock == 0:
        currentProposerBlock -= blockAmount
        if currentProposerBlock < 1:
            currentProposerBlock = 0
        print("\rScanning...", currentProposerBlock, event_time, retryMessage, end ="                        \r")
        retryMessage = ""
        try:
            block_info = json.loads(os.popen('casper-client get-block -b {} --node-address https://rpc.mainnet.casperlabs.io/rpc'.format(currentProposerBlock)).read())
            event_time = datetime.strptime(block_info['result']['block']['header']['timestamp'],'%Y-%m-%dT%H:%M:%S.%fZ')
            if lastDayBlock == 0 and event_time.date() == lastDayMonth:
                lastDayBlock = currentProposerBlock
                while True:
                    currentProposerBlock += 1
                    print("\rScanning...", currentProposerBlock, event_time.time(), retryMessage, end ="                        \r")
                    retryMessage = ""
                    try:
                        block_info = json.loads(os.popen('casper-client get-block -b {} --node-address https://rpc.mainnet.casperlabs.io/rpc'.format(currentProposerBlock)).read())
                        event_time = datetime.strptime(block_info['result']['block']['header']['timestamp'],'%Y-%m-%dT%H:%M:%S.%fZ')
                        if event_time.date() == lastDayMonth:
                            lastDayBlock = currentProposerBlock
                            retryMessage = ""
                        else:
                            blockAmount = 5000
                            currentProposerBlock -= 27 * blockAmount
                            break
                    except:
                        currentProposerBlock -= 1
                        retryMessage = "retrying..."

                print("\rFound  last block for {} at ".format(lastDayMonth), lastDayBlock, end ="                        \n")
            elif event_time.date() == firstDayMonth:
                blockAmount = 100
            elif event_time.date() < firstDayMonth:
                while True:
                    currentProposerBlock += 1
                    print("\rScanning...", currentProposerBlock, event_time.time(), retryMessage, end ="                        \r")
                    retryMessage = ""
                    try:
                        block_info = json.loads(os.popen('casper-client get-block -b {} --node-address https://rpc.mainnet.casperlabs.io/rpc'.format(currentProposerBlock)).read())
                        event_time = datetime.strptime(block_info['result']['block']['header']['timestamp'],'%Y-%m-%dT%H:%M:%S.%fZ')
                        if event_time.date() == firstDayMonth or (event_time.date() > firstDayMonth and currentProposerBlock == 0):
                            firstDayBlock = currentProposerBlock
                            firstDayMonth = event_time.date()
                            break
                    except:
                        currentProposerBlock -= 1
                        retryMessage = "retrying..."
                        
                print("\rFound first block for {} at ".format(event_time.date()), firstDayBlock, end ="                        \n")
            elif currentProposerBlock == 0:
                firstDayBlock = currentProposerBlock
                firstDayMonth = event_time.date()
                print("\rGenesis Block =", firstDayBlock)
                print("\rStart Month   =", firstDayMonth)
                break

        except Exception as e: 
            currentProposerBlock += blockAmount
            retryMessage = "retrying..."

    print("\nDone Searching")

    if output_file != None:
        f = open(output_file, 'w')
        writer = csv.writer(f)
        header = ['Date', 'Block', 'On Hand (liquid)', 'Auction (bid)', 'Total']
        writer.writerow(header)

    startMonth = firstDayMonth
    startBlock = firstDayBlock

    print("Checking Balance...                                                           ")
    firstBalance = checkBalance(startBlock)
    print("Getting Auction Info...")
    firstAuction = getAuctionInfo(startBlock)

    print("Getting Block Info {}".format(startBlock))
    while True:
        try:
            block_info = json.loads(os.popen('casper-client get-block -b {} --node-address https://rpc.mainnet.casperlabs.io/rpc'.format(startBlock)).read())
            event_time = datetime.strptime(block_info['result']['block']['header']['timestamp'],'%Y-%m-%dT%H:%M:%S.%fZ')
            break
        except:
            print("Getting Block Info {}".format(startBlock), "retrying...")

    print("\n\n")
    print("Date\t\t\tBlock\tLiquid\t\tAuction\t\t\tTotal")
    print("{}\t{}\t{} CSPR\t{} CSPR\t{} CSPR".format(event_time.strftime("%Y-%m-%d %H:%M:%S"), startBlock, round(firstBalance/1000000000,num_decimals), round(firstAuction/1000000000,num_decimals), round((firstBalance+firstAuction)/1000000000),num_decimals))

    if output_file != None:
        data = [event_time.strftime("%Y-%m-%d %H:%M:%S"), startBlock, firstBalance/1000000000, firstAuction/1000000000, (firstBalance+firstAuction)/1000000000]
        writer.writerow(data)

    while startMonth < lastDayMonth:
        if startBlock != 0:
            startBlock += int(5200)
        startMonth += timedelta(days=1)
        loop = -1
        while True:
            try:
                startBlock += 1
                loop += 1
                print("\rGetting Block Info ", int(startBlock), event_time.date(), startMonth, retryMessage, end ="                        \r")
                retryMessage = ""
                block_info = json.loads(os.popen('casper-client get-block -b {} --node-address https://rpc.mainnet.casperlabs.io/rpc'.format(int(startBlock))).read())
                event_time = datetime.strptime(block_info['result']['block']['header']['timestamp'],'%Y-%m-%dT%H:%M:%S.%fZ')
                if event_time.date() == startMonth:
                    if loop == 0:
                        while event_time.date() == startMonth:
                            try:
                                # then we went too far... skip backward to find the first block of the day
                                startBlock -= 1
                                print("\rGetting Block Info ", int(startBlock), event_time.date(), startMonth, retryMessage, end ="                        \r")
                                retryMessage = ""
                                block_info = json.loads(os.popen('casper-client get-block -b {} --node-address https://rpc.mainnet.casperlabs.io/rpc'.format(startBlock)).read())
                                event_time = datetime.strptime(block_info['result']['block']['header']['timestamp'],'%Y-%m-%dT%H:%M:%S.%fZ')
                            except:
                                startBlock += 1
                                retryMessage = "retrying..."

                        startBlock += 1
                        while True:
                            try:
                                print("\rGetting Block Info ", int(startBlock), event_time.date(), startMonth, retryMessage, end ="                        \r")
                                retryMessage = ""
                                block_info = json.loads(os.popen('casper-client get-block -b {} --node-address https://rpc.mainnet.casperlabs.io/rpc'.format(startBlock)).read())
                                event_time = datetime.strptime(block_info['result']['block']['header']['timestamp'],'%Y-%m-%dT%H:%M:%S.%fZ')
                                break
                            except:
                                retryMessage = "retrying..."

                    print("\rChecking Balance...            ", end ="                              \r")
                    balance = checkBalance(startBlock)
                    print("\rGetting Auction Info...", end ="                        \r")
                    auction = getAuctionInfo(startBlock)
                    print("\r                                                                                     \r{}\t{}\t{:.2f} CSPR\t{:.2f} CSPR\t{} CSPR".format(event_time.strftime("%Y-%m-%d %H:%M:%S"), startBlock, round(balance/1000000000,num_decimals), round(auction/1000000000,num_decimals), round((balance+auction)/1000000000),num_decimals))
                    if output_file != None:
                        data = [event_time.strftime("%Y-%m-%d %H:%M:%S"), startBlock, balance/1000000000, auction/1000000000, (balance+auction)/1000000000]
                        writer.writerow(data)
                    break
                elif event_time.date() > startMonth:
                    break
            except:
                startBlock -= 1
                loop -= 1
                retryMessage = "retrying..."

    lastBalance = checkBalance(lastDayBlock)
    lastAuction = getAuctionInfo(lastDayBlock)

    block_info = json.loads(os.popen('casper-client get-block -b {} --node-address https://rpc.mainnet.casperlabs.io/rpc'.format(lastDayBlock)).read())
    event_time = datetime.strptime(block_info['result']['block']['header']['timestamp'],'%Y-%m-%dT%H:%M:%S.%fZ')

    print("{}\t{}\t{} CSPR\t{} CSPR\t{} CSPR".format("{}".format(event_time.strftime("%Y-%m-%d %H:%M:%S")), lastDayBlock, round(lastBalance/1000000000,num_decimals), round(lastAuction/1000000000,num_decimals), round((lastBalance+lastAuction)/1000000000),num_decimals))
    if output_file != None:
        data = ["{}".format(event_time.strftime("%Y-%m-%d %H:%M:%S")), lastDayBlock, lastBalance/1000000000, lastAuction/1000000000, (lastBalance+lastAuction)/1000000000]
        writer.writerow(data)

    print("\n\nTotal Increase: {} CSPR\n\n".format(round(((lastBalance+lastAuction) - (firstBalance+firstAuction)) / 1000000000),num_decimals))
    if output_file != None:
        writer.writerow(['', '', 'Total Diff:', 'End - Start', '{}'.format(((lastBalance+lastAuction) - (firstBalance+firstAuction)) / 1000000000)])
        f.close()

#-------------------------------------------------------

def usage():
    print('\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”),')
    print('to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,')
    print('and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:')
    print('The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.')
    print('The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability,')
    print('fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other')
    print('liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings')
    print('in the Software.\n')
    print('Usage: '+sys.argv[0]+' [option]\n')
    print('options:')
    print('\tempty options will do last month')
    print('\tPublic Key will be read locally but can be overriden')
    print('\t\t-k <key>')
    print('\tand if you don\'t have a public key locally you can read it from')
    print('\t\t-l <ip-address> (default = localhost)')
    print('\tto limit decimals')
    print('\t\t-d <num decimals> (default = 2)')
    print('\tStart Dates')
    print('\t\t--sd= (--sd=21)   - Start Date')
    print('\t\t--sm= (--sm=5)    - Start Month')
    print('\t\t--sy= (--sy=2021) - Start Year')
    print('\tEnd Dates')
    print('\t\t--ed= (--ed=21)   - End Date')
    print('\t\t--em= (--em=5)    - End Month')
    print('\t\t--ey= (--ey=2021) - End Year')
    print('\tOutput to file')
    print('\t\t --f= (--f=august.csv)')
    print('\nexample:')
    print('\taudit --sm=2 --em=4 --f=feb-apr.csv\n')

#-------------------------------------------------------

def getPublicKey():
    global public_key
    global localhost
    global start_month
    global start_day
    global start_year
    global last_month
    global last_day
    global last_year
    global output_file
    global num_decimals

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'k:h:l:d:' ,['sm=','sd=','sy=','em=','ed=','ey=','help','f='])
        for opt, arg in opts:
            if opt == '-k':
                public_key = arg
            elif opt == '-l':
                localhost = str(arg)
            elif opt == '--sm':
                start_month = int(arg)
            elif opt == '--sd':
                start_day = int(arg)
            elif opt == '--sy':
                start_year = int(arg)
            elif opt == '--em':
                last_month = int(arg)
            elif opt == '--ed':
                last_day = int(arg)
            elif opt == '--ey':
                last_year = int(arg)
            elif opt == '-d':
                num_decimals = int(opt)
            elif opt == '--f':
                output_file = str(arg)
            elif opt in ('-h', '--help'):
                quit()
    except:
        usage()
        sys.exit(2)

    if not public_key:
        try:
            local_status = json.loads(os.popen('curl -s {}:8888/status'.format(localhost)).read())
            public_key = local_status['our_public_signing_key']
        except:
            reader = open('/etc/casper/validator_keys/public_key_hex')
            try:
                public_key= reader.read().strip()
            finally:
                reader.close()

#-------------------------------------------------------
def notFound(ver):
    print('\nrequired: Casper-Client version 1.3.2 or greater')

    if ver != None:
        print('found   : Casper-Client version {}'.format(ver))

    print('\nClient is incompatible (or not found), please compile (or install) 1.3.2 version or above.\n')
    print('If compiling, these instructions might help')
    print('\tcd casper-node\n\tgit pull\n\tgit checkout release-1.3.2\n\tmake setup-rs\n\tmake build-client-contracts\n\tcargo build -p casper-client --release\n\n\tsudo cp target/release/casper-client /usr/bin\n')

    sys.exit(3)

#-------------------------------------------------------

print('\nAudit - Useful Casper Blockchain tool to get auditable Balance information')
print('The MIT License (MIT)')
print('Copyright (c) 2021 Mark Caldwell (RapidMark)')

try:
    ver = os.popen('casper-client --version').read()
    if not ver:
        notFound(None)
    ver = ver.split()
    if int(ver[2].replace('.', '').split('-')[0]) < 132:
        notFound(ver[2])

except:
    sys.exit(3)


getPublicKey()
run()

