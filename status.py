#!/usr/bin/python3
import sys,os,curses,json,time,select,random,threading,urllib.request,contextlib
from datetime import datetime
from collections import namedtuple
from configparser import ConfigParser

peer_blacklist = []
peer_wrong_chain = []
purse_uref = 0;
global_events = dict()
peer_address = None
finality_signatures = []
missing_validators = []
proposers_dict = dict()
currentProposerBlock = 0
blocks_start = 0
era_rewards_dict = dict()
num_era_rewards = dict()
era_block_start = dict()
our_rewards = []

def system_memory():
    global sysmemory
    sysmemory = curses.newwin(5, 40, 0, 70)
    sysmemory.box()
    box_height, box_width = sysmemory.getmaxyx()
    text_width = box_width - 17 # length of the Text before it gets printed
    sysmemory.addstr(0, 2, 'System Memory', curses.color_pair(4))

    MemInfoEntry = namedtuple('MemInfoEntry', ['value', 'unit'])

    meminfo = {}
    with open('/proc/meminfo') as file:
        for line in file:
            key, value, *unit = line.strip().split()
            meminfo[key.rstrip(':')] = MemInfoEntry(value, unit)

    sysmemory.addstr(1, 2, 'Mem Total  : ', curses.color_pair(1))
    sysmemory.addstr('{:.2f} GB'.format(float(meminfo['MemTotal'].value)/1024/1024), curses.color_pair(4))
    sysmemory.addstr(2, 2, 'Mem Avail  : ', curses.color_pair(1))
    sysmemory.addstr('{:.2f} GB'.format(float(meminfo['MemAvailable'].value)/1024/1024), curses.color_pair(4))

    mem_total = float(meminfo['MemTotal'].value)
    mem_percent = 100*(mem_total-float(meminfo['MemAvailable'].value))/mem_total

    sysmemory.addstr(3, 2, 'Mem Used', curses.color_pair(1))

    for x in range(25):
        sysmemory.addstr(3,13+x,' ', curses.color_pair(6))
    for x in range(int(mem_percent/4)):
        sysmemory.addstr(3,13+x,' ', curses.color_pair(6+int(mem_percent/25)))

    sysmemory.addstr(3, 13, '{:.2f} %'.format(mem_percent), curses.color_pair(11+int(mem_percent/25)))


def system_disk():
    global sysdisk
    sysdisk = curses.newwin(5, 40, 5, 70)
    sysdisk.box()
    box_height, box_width = sysdisk.getmaxyx()
    text_width = box_width - 17 # length of the Text before it gets printed
    sysdisk.addstr(0, 2, 'Disk Usage', curses.color_pair(4))

    result=os.statvfs(node_path)
    block_size=result.f_frsize
    total_blocks=result.f_blocks
    free_blocks=result.f_bfree
    # giga=1024*1024*1024
    giga=1000*1000*1000
    total_size=total_blocks*block_size/giga
    free_size=free_blocks*block_size/giga

    sysdisk.addstr(1, 2, 'Total Disk : ', curses.color_pair(1))
    sysdisk.addstr('{:.2f} GB'.format(float(total_size)), curses.color_pair(4))

    sysdisk.addstr(2, 2, 'Free Space : ', curses.color_pair(1))
    sysdisk.addstr('{:.2f} GB'.format(float(free_size)), curses.color_pair(4))

    disk_percent = 100*float(total_size-free_size)/float(total_size)

    sysdisk.addstr(3, 2, 'Disk Used  : ', curses.color_pair(1))

    for x in range(25):
        sysdisk.addstr(3,13+x,' ', curses.color_pair(6))
    for x in range(int(disk_percent/4)):
        sysdisk.addstr(3,13+x,' ', curses.color_pair(6+int(disk_percent/25)))

    sysdisk.addstr(3, 13, '{:.2f} %'.format(disk_percent), curses.color_pair(11+int(disk_percent/25)))

def casper_bonds():
    global bonds
    bonds = curses.newwin(8, 40, 0, 110)
    bonds.box()
    box_height, box_width = bonds.getmaxyx()
    text_width = box_width - 17 # length of the Text before it gets printed
    bonds.addstr(0, 2, 'Casper Bond Info', curses.color_pair(4))

    try:
        bids = auction_info['bids']
        for item in bids:
            if item['public_key'].strip("\"") == public_key:
                bond_info = item['bid']
                break

        try:
            staked = float(bond_info['staked_amount'].strip("\""))
        except:
            staked = 0
        try:
            inactive = bond_info['inactive']
        except:
            inactive = False
        try:
            delegation = bond_info['delegation_rate']
        except:
            delegation = 0
        try:
            delegates = bond_info['delegators']
            num_delegates = len(delegates)
        except:
            num_delegates = 0

        try:
            delegate_stake = 0
            for d in delegates:
                delegate_stake += float(d['staked_amount'].strip("\""))
        except:
            delegate_stake = 0

        bonds.addstr(1, 2, 'Active       : ', curses.color_pair(1))
        if inactive:
            bonds.addstr('Not Active', curses.color_pair(2 if blink else 20))
        else:
            bonds.addstr('True', curses.color_pair(4))

        bonds.addstr(2, 2, 'Stake        : ', curses.color_pair(1))
        bonds.addstr('{:,.4f} CSPR'.format(staked / 1000000000), curses.color_pair(4))

        bonds.addstr(3, 2, 'Delegation   : ', curses.color_pair(1))
        bonds.addstr('{} %'.format(delegation), curses.color_pair(4))

        bonds.addstr(4, 2, 'Num Delegates: ', curses.color_pair(1))
        bonds.addstr('{}'.format(num_delegates), curses.color_pair(4))

        bonds.addstr(5, 2, 'DelegateStake: ', curses.color_pair(1))
        bonds.addstr('{:,.4f} CSPR'.format(delegate_stake / 1000000000), curses.color_pair(4))

        bonds.addstr(6, 2, 'Total Stake  : ', curses.color_pair(1))
        bonds.addstr('{:,.4f} CSPR'.format((staked + delegate_stake) / 1000000000), curses.color_pair(4))
    except:
        bonds.addstr(1, 2, 'No Bond Info Found', curses.color_pair(1))

class ProposerTask:
    def __init__(self):
        self._running = True

    def terminate(self):
        global_events['terminating'] = 1
        self._running = False

    def run(self):
        loaded1stBlock = False
        global currentProposerBlock
        global blocks_start

        while not loaded1stBlock:
            time.sleep(1)

            try:
                block_info = json.loads(os.popen('casper-client get-block').read())
                currentProposerBlock = int(block_info['result']['block']['header']['height'])
                loaded1stBlock = True
            except:
                pass

        # now that we have the 1st block... loop back X blocks to get a brief history
        xBlocks = 100
        lastBlock = currentProposerBlock - xBlocks
        while currentProposerBlock > lastBlock:
            try:
                block_info = json.loads(os.popen('casper-client get-block -b {}'.format(currentProposerBlock)).read())
                proposer = block_info['result']['block']['body']['proposer'].strip("\"")
                if proposer in proposers_dict:
                    proposers_dict[proposer] = proposers_dict[proposer] + 1
                else:
                    proposers_dict[proposer] = 1

                currentProposerBlock = currentProposerBlock - 1
                blocks_start = blocks_start + 1
            except:
                global_events['proposer loop error'] = 1
                time.sleep(2)
                pass

def getEraInfo(block, currentEra):
    block_info = json.loads(os.popen('casper-client get-era-info-by-switch-block -b {}'.format(block)).read())
    summary = block_info['result']['era_summary']
    if summary != None:
        eraInfo = summary['stored_value']['EraInfo']['seigniorage_allocations']
        currentEra = int(summary['era_id'])
        num_era_rewards[currentEra] = 0
        era_block_start[currentEra] = block

        my_val_reward = 0
        for info in eraInfo:
            if 'Delegator' in info:
                amount = int(info['Delegator']['amount'])
                if currentEra in era_rewards_dict:
                    era_rewards_dict[currentEra] = era_rewards_dict[currentEra] + amount
                else:
                    era_rewards_dict[currentEra] = amount

                num_era_rewards[currentEra] += 1

                # now check if it was us
                val = info['Delegator']['validator_public_key'].strip("\"")
                if val == public_key:
                    my_val_reward += amount

            elif 'Validator' in info:
                amount = int(info['Validator']['amount'])
                if currentEra in era_rewards_dict:
                    era_rewards_dict[currentEra] = era_rewards_dict[currentEra] + amount
                else:
                    era_rewards_dict[currentEra] = amount
    
                num_era_rewards[currentEra] += 1

                # now check if it was us
                val = info['Validator']['validator_public_key'].strip("\"")
                if val == public_key:
                    my_val_reward += amount

        our_rewards.append(my_val_reward)


    return currentEra


class EraTask:
    def __init__(self):
        self._running = True

    def terminate(self):
        global_events['terminating'] = 1
        self._running = False

    def run(self):
        loaded1stBlock = False

        while not loaded1stBlock:
            time.sleep(1)

            try:
                block_info = json.loads(os.popen('casper-client get-block').read())
                currentBlock = int(block_info['result']['block']['header']['height'])
                currentEra = int(block_info['result']['block']['header']['era_id'])
                era_block_start[currentEra] = currentBlock

                loaded1stBlock = True
            except:
                pass

        # now that we have the current era... loop back X eras to get a brief history
        xEras = 10
        lastEra = currentEra - xEras
        while currentBlock > 0 and currentEra > lastEra:
            try:
                currentEra = getEraInfo(currentBlock, currentEra)

                currentBlock = currentBlock - 1
            except:
                global_events['era loop error'] = 1
                global_events['era block '] = currentBlock

                time.sleep(2)
                pass


class EventTask:
    def __init__(self):
        self._running = True

    def terminate(self):
        global_events['terminating'] = 1
        self._running = False

    def has_finality(self):
        timestamp = datetime.now() - self._time_before_read
        if timestamp.seconds > 10 and 'FinalitySignature' in global_events:
            return True

        return False

    def run(self):
        url = 'http://localhost:9999/events'
        localhost_active = False
        while not localhost_active:
            try:
                self._request = urllib.request.Request(url)
                self._reader = urllib.request.urlopen(self._request)
                localhost_active = True
            except:
                time.sleep(10)

        CHUNK = 6 * 1024
        partial_line = ""
        last_block_time = ""

        try:
            while self._running:
                self._time_before_read = datetime.now()
                chunk = self._reader.read(CHUNK)
                if not chunk:
                    break

                if self.has_finality():
                    global_events['FinalitySignature'] = 0
                    finality_signatures.clear()

                data = chunk.decode().split('\n')
                first = True
                for line in data:
                    if first and len(partial_line):
                        line = '{}{}'.format(partial_line, line)
                        partial_line = ""
 
                    if line.startswith('data:'):
                        try:
                            json_str = json.loads(line[5:])
                            key = list(json_str.keys())[0]
                            if key == 'ApiVersion':
                                global_events[key] = json_str[key]
                                continue
                            if key == 'BlockAdded':
                                event_time = datetime.strptime(json_str[key]['block']['header']['timestamp'],'%Y-%m-%dT%H:%M:%S.%fZ')
                                if last_block_time == "":
                                    global_events['Time Since Block'] = 'Calculating'
                                else:
                                    global_events['Time Since Block'] = event_time - last_block_time
                                last_block_time = event_time

                                try:
                                    era_end = json_str[key]['block']['header']['era_end']
                                    if era_end:
                                        reward = era_end['era_report']['rewards']['{}'.format(public_key)]
                                        if (reward > 1000000000):
                                            global_events['Last Reward'] = '{:,.4f} CSPR'.format(reward / 1000000000)
                                        else:
                                            global_events['Last Reward'] = '{:,} mote'.format(int(reward))
                                except:
                                    global_events['Last Reward'] = 'Not Found'

                                try:
                                    proposer = json_str[key]['block']['body']['proposer'].strip("\"")
                                    if proposer in proposers_dict:
                                        proposers_dict[proposer] = proposers_dict[proposer] + 1
                                    else:
                                        proposers_dict[proposer] = 1

                                except:
                                    pass

                                try:
                                    deploy_hashs = json_str[key]['block']['body']['deploy_hashes']
                                    if deploy_hashs:
                                        if 'Deploys' in global_events:
                                            global_events['Deploys'] = global_events['Deploys'] + len(deploy_hashs)
                                        else:
                                            global_events['Deploys'] = len(deploy_hashs)
                                except:
                                    pass

                                try:
                                    transfer_hashs = json_str[key]['block']['body']['transfer_hashes']
                                    if transfer_hashs:
                                        if 'Transfers' in global_events:
                                            global_events['Transfers'] = global_events['Transfers'] + len(transfer_hashs)
                                        else:
                                            global_events['Transfers'] = len(transfer_hashs)
                                except:
                                    pass

                                try:
                                    era_height = json_str[key]['block']['header']['height']
                                    era_id = json_str[key]['block']['header']['era_id']

                                    if era_height:
                                        getEraInfo(era_height, era_id)
                                except:
                                    pass


                            try:
                                if key == 'FinalitySignature':
                                    pub_key = json_str[key]['public_key'].strip("\"")
                                    finality_signatures.append(pub_key)
                            except:
                                pass


                            if key in global_events:
                                global_events[key] = global_events[key] + 1
                            else:
                                global_events[key] = 1
                        except:
                            partial_line = line

            global_events['exiting'] = 1
        except (KeyboardInterrupt, SystemExit):            
            global_events['except'] = 1


def casper_events():
    global events

    local_events = global_events    # make a copy in case our thread tries to stomp
    length = len(local_events.keys())
    events = curses.newwin(2 + (1 if length < 1 else length), 40, 10, 70)
    events.box()
    box_height, box_width = events.getmaxyx()
    text_width = box_width - 17 # length of the Text before it gets printed
    events.addstr(0, 2, 'Casper Events', curses.color_pair(4))

    if length < 1:
        events.addstr(1, 2, 'Waiting for next Event', curses.color_pair(5))
    else:
        index = 0
        for key in list(sorted(local_events.keys())):
            events.addstr(1+index, 2, '{} : '.format(key.ljust(17, ' ')), curses.color_pair(1))
            events.addstr('{}'.format(local_events[key]), curses.color_pair(4))
            index = index + 1

def casper_proposers():
    global proposers

    local_proposers = proposers_dict    # make a copy in case our thread tries to stomp

    max_proposers = 20
    we_are_included = False
    for proposer in sorted(local_proposers.items(), key=lambda x: x[1], reverse=True):
        if proposer[0] == public_key:
            we_are_included = True
            break

    length = min(len(local_proposers.keys()), max_proposers)
    window_length = length + (0 if we_are_included else 1)
    starty = 18+ 2 + (1 if len(global_events.keys()) < 1 else len(global_events.keys()))

    proposers= curses.newwin(2 + (1 if window_length < 1 else window_length), 40, 8, 110)

    proposers.box()
    box_height, box_width = proposers.getmaxyx()
    text_width = box_width - 17 # length of the Text before it gets printed
    proposers.addstr(0, 2, 'Last', curses.color_pair(4))
    proposers.addstr(' {:6} '.format((global_height-currentProposerBlock) if global_height > 0 and currentProposerBlock > 0 else 0), curses.color_pair(5))
    proposers.addstr('Blks / Stk Wgt / Prpsr %', curses.color_pair(4))


    index = 1
    try:
        blocks = global_events['BlockAdded'] + blocks_start
    except:
        blocks = 1 if blocks_start < 1 else blocks_start

    if not length:
        proposers.addstr(index, 2, 'Waiting for next Event', curses.color_pair(5))
    else:
        total_staked = 0
        for item in current_weights.items():
            total_staked += item[1] 

        we_are_included = False
        for proposer in sorted(local_proposers.items(), key=lambda x: x[1], reverse=True):
            proposers.addstr(index, 2, '{}....{} : '.format(proposer[0][:6], proposer[0][-6:]), curses.color_pair(1 if proposer[0] != public_key else 5))
#           proposers.addstr('{:6.2f}%'.format(current_weights[proposer[0]]/3500000000000000000*100), curses.color_pair(4))
            proposers.addstr('{:6.2f}%'.format(current_weights[proposer[0]]/total_staked*100), curses.color_pair(4))
            proposers.addstr(' / ', curses.color_pair(1))
            proposers.addstr('{:6.2f}%'.format(100*proposer[1]/blocks), curses.color_pair(4))

            index += 1

            if proposer[0] == public_key:
                we_are_included = True

            if index > max_proposers:
                break


        if not we_are_included and public_key in current_weights:            
            proposers.addstr(index, 2, '{}....{} : '.format(public_key[:6], public_key[-6:]), curses.color_pair(5))
            if public_key in local_proposers:
                proposers.addstr('{:6.2f}%'.format(current_weights[public_key]/3500000000000000000*100), curses.color_pair(4))
                proposers.addstr(' / ', curses.color_pair(1))
                proposers.addstr('{:6.2f}%'.format(100*local_proposers[public_key]/blocks), curses.color_pair(4))
            else:
                proposers.addstr('{:6.2f}%'.format(current_weights[public_key]/3500000000000000000*100), curses.color_pair(4))
                proposers.addstr(' / ', curses.color_pair(1))
                proposers.addstr('{:6.2f}%'.format(0), curses.color_pair(4))

def casper_era_rewards():
    global era_rewards

    events_box_y, events_box_x = events.getbegyx()
    events_box_height, events_box_width = events.getmaxyx()

    max_print = 10

    length = min(len(era_rewards_dict), max_print)
    era_rewards = curses.newwin(2 + (length*2)+1, events_box_width, events_box_y+events_box_height, events_box_x)

    era_rewards.box()
    box_height, box_width = era_rewards.getmaxyx()
    text_width = box_width - 17 # length of the Text before it gets printed
    era_rewards.addstr(0, 2, 'Average Era Rewards / Blocks', curses.color_pair(4))

    current_print = 0
    index = 1
    for era in sorted(era_rewards_dict.items(), key=lambda x: x[0], reverse=True):
        era_rewards.addstr(index, 2, '{} Reward : '.format(era[0]), curses.color_pair(1))
        era_rewards.addstr('{:10,.4f} CSPR'.format((era[1]/num_era_rewards[era[0]]) / 1000000000), curses.color_pair(4))
        index += 1
        current_print += 1

        if current_print >= max_print:
            break

    era_rewards.addstr(index, 2, '--------', curses.color_pair(5))
    index += 1

    current_print = 0
    for era in sorted(era_block_start.items(), key=lambda x: x[0], reverse=True):
        diff = 0
        next_era = era[0]-1

        if next_era in era_block_start:
            diff = era[1] - era_block_start[next_era]

        if diff != 0:
            era_rewards.addstr(index, 2, '{} Blocks : '.format(era[0]), curses.color_pair(1))
            era_rewards.addstr('{:5}'.format(diff), curses.color_pair(4))
            index += 1
            current_print += 1

        if current_print >= max_print:
            break


def casper_finality():
    global finality

    local_events = global_events    # make a copy in case our thread tries to stomp
    length = len(local_events.keys())
    starty = 18+ 2 + (1 if length < 1 else length)

    missing_val = len(missing_validators)

    finality= curses.newwin(2 + (1 if missing_val < 1 else missing_val), 40, starty, 70)

    finality.box()
    box_height, box_width = finality.getmaxyx()
    text_width = box_width - 17 # length of the Text before it gets printed
    finality.addstr(0, 2, 'Validators Not Finalized', curses.color_pair(4))
    
    index = 1
    if not len(missing_validators):
        finality.addstr(index, 2, 'Checking Finality Signatures' if length > 0 else 'Waiting for next Event', curses.color_pair(5))
    else:
        for missing in missing_validators:
            finality.addstr(index, 2, '{}....{}'.format(missing[:16], missing[-16:]), curses.color_pair(1 if missing != public_key else 2 if blink else 20))
            index = index + 1


def casper_peers():
    global peers
    peers = curses.newwin(5, 70, 33, 0)
    peers.box()
    box_height, box_width = peers.getmaxyx()
    text_width = box_width - 17 # length of the Text before it gets printed
    peers.addstr(0, 2, 'Casper Peers', curses.color_pair(4))

    try:
        num_peers = len(local_status['peers'])
    except:
        num_peers = 0

    peers.addstr(1, 2, 'Peers        : ', curses.color_pair(1))
    peers.addstr('{}'.format(num_peers), curses.color_pair(4))

    peers.addstr(2, 2, 'In Blacklist : ', curses.color_pair(1))
    peers.addstr('{}'.format(len(peer_blacklist)), curses.color_pair(4))
    peers.addstr('\t<- Not answering our :8888/status', curses.color_pair(1))

    peers.addstr(3, 2, 'Bad Chainspec: ', curses.color_pair(1))
    peers.addstr('{}'.format(len(peer_wrong_chain)), curses.color_pair(4))
    peers.addstr('\t<- Not on our Chainspec (', curses.color_pair(1))
    peers.addstr('{}'.format(local_chainspec), curses.color_pair(4))
    peers.addstr(')', curses.color_pair(1))

#    peers.addstr(4, 2,'{}'.format(peer_blacklist)[:347], curses.color_pair(4))

def casper_launcher():
    global launcher
    launcher = curses.newwin(7, 70, 0, 0)
    launcher.box()
    box_height, box_width = launcher.getmaxyx()
    text_width = box_width - 17 # length of the Text before it gets printed
    launcher.addstr(0, 2, 'Casper Node Launcher', curses.color_pair(4))

    key_value = os.popen('systemctl show casper-node-launcher.service | grep -e MemoryCurrent -e ActiveState -e LoadState -e FragmentPath -e StateChangeTimestamp=').read().split('\n')
    json_dict = {}
    for entry in key_value:
        kv = entry.split("=", 1)
        if len(kv) == 2:
            json_dict[kv[0]] = kv[1][:text_width]

    index = 1;

    try:
        memory = json_dict['MemoryCurrent']
    except:
        memory = 'null'
    try:
        active = json_dict['ActiveState']
    except:
        active = 'null'
    try:
        load = json_dict['LoadState']
    except:
        load = 'null'
    try:
        fragment = json_dict['FragmentPath']
    except:
        fragment = 'null'
    try:
        timestamp = json_dict['StateChangeTimestamp']
        target = datetime.strptime(timestamp,'%a %Y-%m-%d %H:%M:%S %Z')
        now = datetime.now()
        timestamp = now - target
    except:
        timestamp = 'null'

    if active == 'active':
        launcher.addstr(1, 2, 'MemoryCurrent: ', curses.color_pair(1))
        launcher.addstr('{}'.format(memory), curses.color_pair(4))

        launcher.addstr(2, 2, 'ActiveState  : ', curses.color_pair(1))
        launcher.addstr('{}'.format(active), curses.color_pair(4))

        launcher.addstr(3, 2, 'LoadState    : ', curses.color_pair(1))
        launcher.addstr('{}'.format(load), curses.color_pair(4))
    
        launcher.addstr(4, 2, 'FragmentPath : ', curses.color_pair(1))
        launcher.addstr('{}'.format(fragment), curses.color_pair(4))

        launcher.addstr(5, 2, 'Running Time : ', curses.color_pair(1))
        launcher.addstr('{}'.format(timestamp), curses.color_pair(4))
    else:
        launcher.addstr(1, 2, 'Casper-Node-Launcher not running', curses.color_pair(2))



def casper_block_info():
    global block_info
    global global_height
    block_info = curses.newwin(15, 70, 7, 0)
    block_info.box()
    box_height, box_width = block_info.getmaxyx()
    text_width = box_width - 17 # length of the Text before it gets printed
    block_info.addstr(0, 2, 'Casper Block Info', curses.color_pair(4))

    global local_status
    local_status = 'null'

    global local_chainspec
    local_chainspec = 'null'

    try:
        local_status = json.loads(os.popen('curl -s localhost:8888/status').read())
        local_chainspec = local_status['chainspec_name']

        last_added_block_info = local_status['last_added_block_info']
        try:
            global_height = local_height = last_added_block_info['height']
        except:
            global_height = 0
            local_height = 'null'
        try:
            round_length = local_status['round_length']
        except:
            round_length = 'null'
        try:
            next_upgrade = local_status['next_upgrade']
            if next_upgrade != None:
                next_upgrade = 'Era: {} - Version: {}'.format(next_upgrade['activation_point'], next_upgrade['protocol_version'])
        except:
            next_upgrade = 'null'
        try:
            build_version = local_status['build_version']
        except:
            build_version = 'null'
        try:
            chain_name = local_status['chainspec_name']
        except:
            chain_name = 'null'
        try:
            root_hash = local_status['starting_state_root_hash']
        except:
            root_hash = 'null'
        try:
            api_version = local_status['api_version']
        except:
            api_version = 'null'
        try:
            local_era = last_added_block_info['era_id']
        except:
            local_era = 'null'
    except:
        global_height = 0
        local_height = 'null'
        round_length = 'null'
        next_upgrade = 'null'
        build_version= 'null'
        chain_name = 'null'
        root_hash = 'null'
        api_version = 'null'
        local_era = 'null'
        local_chainspe = 'null'

    global peer_address
    previous_peer = peer_address

    try:
        peer_to_use_as_global = random.choice(local_status['peers'])
        peer_address = peer_to_use_as_global['address'].split(':')[0]
        if peer_address in peer_blacklist or peer_address in peer_wrong_chain:
            peer_address = previous_peer
    except:
        peer_address = previous_peer

    if peer_address:
        try:
            try:
                peer_status = json.loads(os.popen('curl -m 2 -s {}:8888/status'.format(peer_address)).read())
                peer_chainspec = peer_status['chainspec_name']
                if peer_chainspec != local_chainspec:
                    peer_address = previous_peer
                    if peer_address not in peer_wrong_chain:
                        peer_wrong_chain.append(peer_address)
                    
            except:
                if peer_address not in peer_blacklist:
                    peer_blacklist.append(peer_address)
                if previous_peer:
                    peer_address = previous_peer
                    peer_status = json.loads(os.popen('curl -m 2 -s {}:8888/status'.format(peer_address)).read())

            peer_height = peer_status['last_added_block_info']['height']
        except:
            peer_height = 'null'
    else:
        peer_height = 'null'


    index = 1
    block_info.addstr(index, 2, 'Local height : ', curses.color_pair(1))
    block_info.addstr('{}'.format(local_height), curses.color_pair(4))

    index += 1
    block_info.addstr(index, 2, 'Peer height  : ', curses.color_pair(1))
    block_info.addstr('{}\t\t'.format(peer_height), curses.color_pair(4))

    block_info.addstr('<- From Peer : ', curses.color_pair(1))
    block_info.addstr('{}'.format(peer_address), curses.color_pair(4))

    index += 1
    block_info.addstr(index, 2, 'Round Length : ', curses.color_pair(1))
    block_info.addstr('{}'.format(round_length), curses.color_pair(4))
    index += 1
    block_info.addstr(index, 2, 'Next Upgrade : ', curses.color_pair(1))
    block_info.addstr('{}'.format(next_upgrade), curses.color_pair(4 if next_upgrade == None else 5))
    index += 1
    block_info.addstr(index, 2, 'Build Version: ', curses.color_pair(1))
    block_info.addstr('{}'.format(build_version), curses.color_pair(4))

    index += 2
    block_info.addstr(index, 2, 'Chain Name   : ', curses.color_pair(1))
    block_info.addstr('{}'.format(chain_name), curses.color_pair(4))
    index += 1
    block_info.addstr(index, 2, 'Starting Hash: ', curses.color_pair(1))
    block_info.addstr('{}'.format(root_hash), curses.color_pair(4))

    index += 2
    block_info.addstr(index, 2, 'API Version  : ', curses.color_pair(1))
    block_info.addstr('{}'.format(api_version), curses.color_pair(4))
    index += 1
    block_info.addstr(index, 2, 'Local ERA    : ', curses.color_pair(1))
    block_info.addstr('{}'.format(local_era), curses.color_pair(4))

    avg_num_blocks = 110
    bar_length = 40
    block_percent = 1

    if local_era in era_block_start and  local_era-1 in era_block_start:
        block_percent = int((era_block_start[local_era]-era_block_start[local_era-1])/avg_num_blocks*100)

    if block_percent > 99:
        block_percent = 100

    for x in range(bar_length):
        block_info.addstr(index,28+x,' ', curses.color_pair(6))

    num_blocks = int(float(block_percent/(100/bar_length)))
    for x in range(num_blocks):
        block_info.addstr(index,28+x,' ', curses.color_pair(16))

    index += 2
    block_info.addstr(index, 2, 'Storage Path : ', curses.color_pair(1))
    block_info.addstr('{}'.format(node_path), curses.color_pair(4))

def casper_public_key():
    global pub_key_win
    global current_era_global
    pub_key_win = curses.newwin(4, 70, 22, 0)
    pub_key_win.box()
    box_height, box_width = pub_key_win.getmaxyx()
    text_width = box_width - 17 # length of the Text before it gets printed

    pub_key_win.addstr(0, 2, 'Public Key', curses.color_pair(4))
    pub_key_win.addstr(1, 2, '{}'.format(public_key), curses.color_pair(1))
    pub_key_win.addstr(2, 2, 'Balance      : ', curses.color_pair(1))

    try:
        block_info = json.loads(os.popen('casper-client get-block').read())
        header_info = block_info['result']['block']['header']
        lfb_root = header_info['state_root_hash']
        currentBlock = int(header_info['height'])
        current_era_global = int(header_info['era_id'])
        era_block_start[current_era_global] = currentBlock

        global purse_uref   # we only need to get this ref the first time
        if purse_uref == 0:
            query_state = json.loads(os.popen('casper-client query-state -k "{}" -s "{}"'.format(public_key, lfb_root)).read())
            purse_uref = query_state['result']['stored_value']['Account']['main_purse']

        balance_json = json.loads(os.popen('casper-client get-balance --purse-uref "{}" --state-root-hash "{}"'.format(purse_uref, lfb_root)).read())
        balance = int(balance_json['result']['balance_value'].strip("\""))

        if (balance > 1000000000):
            pub_key_win.addstr('{:,.9f} CSPR'.format(balance / 1000000000), curses.color_pair(4))
        else:
            pub_key_win.addstr('{:,} mote'.format(balance), curses.color_pair(4))

    except:
        current_era_global = 0
        pub_key_win.addstr('Not available yet', curses.color_pair(2))


def casper_validator():
    global validator
    validator = curses.newwin(7, 70, 26, 0)
    validator.box()
    box_height, box_width = validator.getmaxyx()
    text_width = box_width - 17 # length of the Text before it gets printed
    validator.addstr(0, 2, 'Casper Validator Info', curses.color_pair(4))

    local_era = 0
    try:
        last_added_block_info = local_status['last_added_block_info']

        try:
            local_era = last_added_block_info['era_id']
        except:
            local_era = 0
    except:
        local_era = 0

    current_era = future_era = 0
    current_weight = future_weight = 0
    num_cur_validators = num_fut_validators = 0
    current_index = future_index = 0

    try:
        global auction_info
        global current_weights
        current_weights = dict()
        future = dict()

        auction_info = json.loads(os.popen('casper-client get-auction-info').read())
        auction_info = auction_info['result']['auction_state']        
    
        current_validators = auction_info['era_validators'][0]['validator_weights']
        current_era = auction_info['era_validators'][0]['era_id']
        for item in current_validators:
            key = item['public_key'].strip("\"");
            value = int(item['weight'].strip("\""))
            current_weights[key] = value
            if key == public_key:
                current_weight = value

        missing_validators.clear()
        if event_ptr.has_finality():
            for key in current_weights.keys():
                if key not in finality_signatures:
                    missing_validators.append(key)

        future_validators = auction_info['era_validators'][1]['validator_weights']
        future_era = auction_info['era_validators'][1]['era_id']
        for item in future_validators:
            key = item['public_key'].strip("\"");
            value = int(item['weight'].strip("\""))
            future[key] = value
            if key == public_key:
                future_weight = value

        #arg... indexing a sorted is not working... so I'll just iterate for now...
        index = 1
        for item in sorted(current_weights.items(), key=lambda x: x[1], reverse=True):
            if item[0] == public_key:
                current_index = index
                break
            index += 1

        index = 1
        for item in sorted(future.items(), key=lambda x: x[1], reverse=True):
            if item[0] == public_key:
                future_index = index
                break
            index += 1

        num_cur_validators = len(current_validators)
        num_fut_validators = len(current_validators)

    except:
        current_weight = 0
        future_weight = 0
        current_validators = 0
        current_era = 0
        pass

    validator.addstr(1, 2, 'Validators   : ', curses.color_pair(1))
    validator.addstr('{:,} / {:,} / {}'.format(num_cur_validators, num_fut_validators,validator_slots), curses.color_pair(4))
    validator.addstr(1, 42, '<- ERA {}/{}/Slots'.format(current_era, future_era), curses.color_pair(1))

    # get the length of the printed string so we can right justify and not leave blank spaces
    if current_weight > 100000000000000:
        current_str = '{:,.4f} CSPR'.format(current_weight/1000000000)
    else:
        current_str = '{:,.9f} CSPR'.format(current_weight/1000000000)

    if future_weight > 100000000000000:
        future_str = '{:,.4f} CSPR'.format(future_weight/1000000000)
    else:
        future_str = '{:,.9f} CSPR'.format(future_weight/1000000000)

    longest_len = max(len(current_str), len(future_str))

    global money_string_length
    money_string_length = longest_len

    validator.addstr(2, 2, 'ERA {} : '.format(str(current_era).ljust(8, ' ')), curses.color_pair(1))
    validator.addstr('{}'.format(current_str.rjust(longest_len, ' ')), curses.color_pair(4))
    validator.addstr(2, 42, '<- Position {}'.format(current_index), curses.color_pair(1))

    validator.addstr(3, 2, 'ERA {} : '.format(str(future_era).ljust(8, ' ')), curses.color_pair(1))
    validator.addstr('{}'.format(future_str.rjust(longest_len, ' ')), curses.color_pair(4))
    validator.addstr(3, 42, '<- Position {}'.format(future_index), curses.color_pair(1))

    validator.addstr(4, 2, 'Last Reward  : ', curses.color_pair(1))
    reward = float(future_weight - current_weight)
    if (reward > 1000000000):
        this_str = '{:,.4f} CSPR'.format(reward / 1000000000)
    else:
        this_str = '{:,} mote'.format(int(reward))
    validator.addstr('{}'.format(this_str.rjust(longest_len, ' ')), curses.color_pair(4))

    validator.addstr(5, 2, 'Avg Reward   : ', curses.color_pair(1))
    reward = 0
    if len(our_rewards):
        reward = float(sum(our_rewards) / len(our_rewards))
    if reward > 1000000000:
        this_str = '{:,.4f} CSPR'.format(reward / 1000000000)
    else:
        this_str = '{:,} mote'.format(int(reward))
    validator.addstr('{}'.format(this_str.rjust(longest_len, ' ')), curses.color_pair(4))
    validator.addstr(5, 42, '<- Last {} reward{}'.format(len(our_rewards), 's' if len(our_rewards)>1 else ''), curses.color_pair(1))



def draw_menu(casper):
    k = 0
    cursor_x = 0
    cursor_y = 0

    # Clear and refresh the screen for a blank canvas
    casper.clear()
    casper.refresh()

    global main_window
    main_window = casper

    # Start colors in curses
    curses.start_color()
    curses.init_pair( 1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair( 2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair( 3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair( 4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair( 5, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    curses.init_pair( 6, curses.COLOR_GREEN, curses.COLOR_WHITE)
    curses.init_pair( 7, curses.COLOR_WHITE, curses.COLOR_CYAN)
    curses.init_pair( 8, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    curses.init_pair( 9, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_WHITE)

    curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(12, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(13, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(14, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(15, curses.COLOR_BLACK, curses.COLOR_WHITE)

    curses.init_pair(16, curses.COLOR_BLACK, curses.COLOR_GREEN)

    curses.init_pair(20, curses.COLOR_RED, curses.COLOR_WHITE)

    global blink
    blink = False
    
    config.read('/etc/casper/1_0_0/chainspec.toml')
    global validator_slots
    validator_slots = config.get('core', 'validator_slots').strip('\'')


    # Loop where k is the last character pressed
    while (k != ord('q')):

        # Initialization
        casper.erase()
        casper.noutrefresh()
        global main_height
        global main_width
        main_height, main_width = casper.getmaxyx()

        blink = blink ^ True

        cursor_x = main_width-1
        cursor_y = main_height-1

        casper_launcher()
        casper_block_info()
        casper_public_key()
        casper_validator()
        casper_peers()
        system_memory()
        system_disk()
        casper_bonds()
        casper_events()
        casper_era_rewards()
        casper_proposers()

        # Render status bar
        statusbarstr = "Press 'ctrl-c' to exit | STATUS BAR "
        casper.attron(curses.color_pair(3))
        casper.addstr(main_height-1, 1, statusbarstr)
        casper.addstr(main_height-1, len(statusbarstr), " " * (main_width - len(statusbarstr) - 1))
        casper.attroff(curses.color_pair(3))

        # Refresh the screen

        launcher.noutrefresh()
        block_info.noutrefresh()
        pub_key_win.noutrefresh()
        validator.noutrefresh()
        sysmemory.noutrefresh()
        peers.noutrefresh()
        sysdisk.noutrefresh()
        bonds.noutrefresh()
        events.noutrefresh()
        era_rewards.noutrefresh()
        proposers.noutrefresh()
        casper.noutrefresh()

        curses.doupdate()

        try:
            time.sleep(1)
        except KeyboardInterrupt:
            event_ptr.terminate()
            break;

        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            k = casper.getch()

def main():
    os.environ['NCURSES_NO_UTF8_ACS'] = '1'

    global config
    config = ConfigParser()
    config.read('/etc/casper/1_0_0/config.toml')
    global node_path
    node_path = config.get('storage', 'path').strip('\'')
    
    global random
    random = random.SystemRandom()

    global public_key

    try:
        local_status = json.loads(os.popen('curl -s localhost:8888/status').read())
        public_key = local_status['our_public_signing_key']
    except:
        reader = open('/etc/casper/validator_keys/public_key_hex')
        try:
            public_key= reader.read().strip()
        finally:
            reader.close()

    global thread_ptr
    global event_ptr
    event_ptr = EventTask()
    thread_ptr = threading.Thread(target=event_ptr.run)
    thread_ptr.daemon = True
    thread_ptr.start()

    global proposer_thread_ptr
    global proposer_ptr
    proposer_ptr = ProposerTask()
    proposer_thread_ptr = threading.Thread(target=proposer_ptr.run)
    proposer_thread_ptr.daemon = True
    proposer_thread_ptr.start()

    global era_thread_ptr
    global era_ptr
    era_ptr = EraTask()
    era_thread_ptr = threading.Thread(target=era_ptr.run)
    era_thread_ptr.daemon = True
    era_thread_ptr.start()

    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()
