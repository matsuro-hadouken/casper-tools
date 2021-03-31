#!/usr/bin/python3
import sys,os,curses,json,time,select,random
from datetime import datetime
from collections import namedtuple
from configparser import ConfigParser

peer_blacklist = []
purse_uref = 0;

def system_memory():
    global sysmemory
    sysmemory = curses.newwin(5, 40, 0, 71)
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

    sysmemory.addstr(1, 2, 'MemTotal : ', curses.color_pair(1))
    sysmemory.addstr('{:.2f} GB'.format(float(meminfo['MemTotal'].value)/1024/1024), curses.color_pair(4))
    
    sysmemory.addstr(2, 2, 'MemAvail : ', curses.color_pair(1))

    sysmemory.addstr('{:.2f} GB'.format(float(meminfo['MemAvailable'].value)/1024/1024), curses.color_pair(4))

    mem_total = float(meminfo['MemTotal'].value)
    mem_percent = 100*(mem_total-float(meminfo['MemAvailable'].value))/mem_total

    curses.start_color()
    curses.init_pair( 6, 2, 7)
    curses.init_pair( 7, 7, 6)
    curses.init_pair( 8, 7, 3)
    curses.init_pair( 9, 7, 1)
    curses.init_pair(10, 0, 7)

    curses.init_pair(11, 0, 7)
    curses.init_pair(12, 0, 6)
    curses.init_pair(13, 0, 3)
    curses.init_pair(14, 0, 1)
    curses.init_pair(15, 0, 7)

    sysmemory.addstr(3, 2, 'MemUsed  : ', curses.color_pair(1))

    for x in range(25):
        sysmemory.addstr(3,13+x,' ', curses.color_pair(6))
    for x in range(int(mem_percent/4)):
        sysmemory.addstr(3,13+x,' ', curses.color_pair(6+int(mem_percent/25)))

    sysmemory.addstr(3, 13, '{:.2f} %'.format(mem_percent), curses.color_pair(11+int(mem_percent/25)))


def system_disk():
    global sysdisk
    sysdisk = curses.newwin(5, 40, 5, 71)
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
    bonds = curses.newwin(8, 40, 10, 71)
    bonds.box()
    box_height, box_width = bonds.getmaxyx()
    text_width = box_width - 17 # length of the Text before it gets printed
    bonds.addstr(0, 2, 'Capser Bond Info', curses.color_pair(4))

#    casper-client get-auction-info --node-address http://13.58.71.180:7777 | jq -r '.result.auction_state.bids[] | select(.public_key=="01cb70f16e5dbfc0c0601cd6fe3d9e04e815eaebfe3e563f3d48e8035a4b8f18e2")'

    try:
        bond_info = json.loads(os.popen('casper-client get-auction-info | jq -r \'.result.auction_state.bids[]? | select(.public_key=="{}")\''.format(public_key)).read())
        try:
            staked = float(bond_info['bid']['staked_amount'].strip("\""))
        except:
            staked = 0
        try:
            inactive = bond_info['bid']['inactive']
        except:
            inactive = False
        try:
            delegation = bond_info['bid']['delegation_rate']
        except:
            delegation = 0
        try:
            delegates = bond_info['bid']['delegators']
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
            bonds.addstr('Not Active', curses.color_pair(2))
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


def casper_peers():
    global peers
    peers = curses.newwin(10, 70, 31, 0)
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

    config.read('/etc/casper/1_0_0/chainspec.toml')
    validator_slots = config.get('core', 'validator_slots').strip('\'')

    peers.addstr(2, 2, 'Num Val Slots: ', curses.color_pair(1))
    peers.addstr('{}'.format(validator_slots), curses.color_pair(4))

    peers.addstr(3, 2, 'In Blacklist : ', curses.color_pair(1))
    peers.addstr('{}'.format(len(peer_blacklist)), curses.color_pair(4))
    peers.addstr('\t<- Not answering our :8888/status', curses.color_pair(1))

    peers.addstr(4, 2,'{}'.format(peer_blacklist)[:347], curses.color_pair(4))

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


def casper_block_info():
    global block_info
    block_info = curses.newwin(15, 70, 7, 0)
    block_info.box()
    box_height, box_width = block_info.getmaxyx()
    text_width = box_width - 17 # length of the Text before it gets printed
    block_info.addstr(0, 2, 'Casper Block Info', curses.color_pair(4))

    try:
        global local_status
        local_status = json.loads(os.popen('curl -s localhost:8888/status').read())

        last_added_block_info = local_status['last_added_block_info']
        try:
            local_height = last_added_block_info['height']
        except:
            local_height = 'null'
        try:
            round_length = local_status['round_length']
        except:
            round_length = 'null'
        try:
            next_upgrade = local_status['next_upgrade']
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
        local_height = 'null'
        round_length = 'null'
        next_upgrade = 'null'
        build_version= 'null'
        chain_name = 'null'
        root_hash = 'null'
        api_version = 'null'
        local_era = 'null'


    try:
        peer_to_use_as_global = random.choice(local_status['peers'])
        peer_address = peer_to_use_as_global['address'].split(':')[0]
        if peer_address in peer_blacklist: # then do it again (but don't loop forever, just do it once)
            peer_to_use_as_global = random.choice(local_status['peers'])
            peer_address = peer_to_use_as_global['address'].split(':')[0]

    except:
        peer_address = 'null'

    if peer_address != 'null':
        try:
            try:
                global_status = json.loads(os.popen('curl -m 2 -s {}:8888/status | jq -r .last_added_block_info'.format(peer_address)).read())
            except:
                if peer_address not in peer_blacklist:
                    peer_blacklist.append(peer_address)
            global_height = global_status['height']
        except:
            global_height = 'null'
    else:
        global_height = 'null'


    index = 1
    block_info.addstr(index, 2, 'Local height : ', curses.color_pair(1))
    block_info.addstr('{}'.format(local_height), curses.color_pair(4))

    index += 1
    block_info.addstr(index, 2, 'Peer height  : ', curses.color_pair(1))
    block_info.addstr('{}\t\t'.format(global_height), curses.color_pair(4))

    block_info.addstr('<- From Peer : ', curses.color_pair(1))
    block_info.addstr('{}'.format(peer_address), curses.color_pair(4))

    index += 1
    block_info.addstr(index, 2, 'Round Length : ', curses.color_pair(1))
    block_info.addstr('{}'.format(round_length), curses.color_pair(4))
    index += 1
    block_info.addstr(index, 2, 'Next Upgrade : ', curses.color_pair(1))
    block_info.addstr('{}'.format(next_upgrade), curses.color_pair(4))
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

    index += 2
    block_info.addstr(index, 2, 'Storage Path : ', curses.color_pair(1))
    block_info.addstr('{}'.format(node_path), curses.color_pair(4))

def casper_public_key():
    global pub_key_win
    pub_key_win = curses.newwin(4, 70, 22, 0)
    pub_key_win.box()
    box_height, box_width = pub_key_win.getmaxyx()
    text_width = box_width - 17 # length of the Text before it gets printed
    pub_key_win.addstr(0, 2, 'Public Key', curses.color_pair(4))

    pub_key_win.addstr(1, 2, '{}'.format(public_key), curses.color_pair(1))

    pub_key_win.addstr(2, 2, 'Balance  : ', curses.color_pair(1))

    try:
        block_info = json.loads(os.popen('casper-client get-block').read())
        lfb_root = block_info['result']['block']['header']['state_root_hash']

        global purse_uref   # we only need to get this ref the first time
        if purse_uref == 0:
            query_state = json.loads(os.popen('casper-client query-state -k "{}" -s "{}"'.format(public_key, lfb_root)).read())
            purse_uref = query_state['result']['stored_value']['Account']['main_purse']

        balance_json = json.loads(os.popen('casper-client get-balance --purse-uref "{}" --state-root-hash "{}"'.format(purse_uref, lfb_root)).read())
        balance = float(balance_json['result']['balance_value'].strip("\""))

        if (balance > 1000000000):
            pub_key_win.addstr('{:,.4f} CSPR'.format(balance / 1000000000), curses.color_pair(4))
        else:
            pub_key_win.addstr('{:,} mote'.format(balance), curses.color_pair(4))
    except:
        pub_key_win.addstr('Not available yet', curses.color_pair(2))


def casper_validator():
    global validator
    validator = curses.newwin(6, 70, 26, 0)
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

    try:
        era_current_weight = json.loads(os.popen('casper-client get-auction-info | jq -r \'.result.auction_state.era_validators | .[0].validator_weights[]? | select(.public_key=="{}")| .weight\''.format(public_key)).read())
        era_future_weight  = json.loads(os.popen('casper-client get-auction-info | jq -r \'.result.auction_state.era_validators | .[1].validator_weights[]? | select(.public_key=="{}")| .weight\''.format(public_key)).read())
    except:
        era_current_weight = 0;
        era_future_weight = 0;

    validator.addstr(1, 2, 'ERA {}       : '.format(local_era), curses.color_pair(1))
    validator.addstr('{:,.4f} CSPR'.format(era_current_weight/1000000000, era_current_weight), curses.color_pair(4))

    validator.addstr(2, 2, 'ERA {}       : '.format(local_era+1), curses.color_pair(1))
    validator.addstr('{:,.4f} CSPR'.format(era_future_weight/1000000000), curses.color_pair(4))

    validator.addstr(4, 2, 'Last Reward : ', curses.color_pair(1))
    reward = float(era_future_weight - era_current_weight)
    if (reward > 1000000000):
        validator.addstr('{:,.4f} CSPR'.format(reward / 1000000000), curses.color_pair(4))
    else:
        validator.addstr('{:,} mote'.format(reward), curses.color_pair(4))


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
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    global public_key
    public_key=os.popen('curl -s localhost:8888/status | jq -r .our_public_signing_key').read().split('\n')[0]


    # Loop where k is the last character pressed
    while (k != ord('q')):

        # Initialization
#        casper.clear()
        global main_height
        global main_width
        main_height, main_width = casper.getmaxyx()

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

        # Render status bar
        statusbarstr = "Press 'ctrl-c' to exit | STATUS BAR "
        casper.attron(curses.color_pair(3))
        casper.addstr(main_height-1, 1, statusbarstr)
        casper.addstr(main_height-1, len(statusbarstr), " " * (main_width - len(statusbarstr) - 1))
        casper.attroff(curses.color_pair(3))

        # Refresh the screen

        launcher.refresh()
        block_info.refresh()
        pub_key_win.refresh()
        validator.refresh()
        sysmemory.refresh()
        peers.refresh()
        sysdisk.refresh()
        bonds.refresh()
        casper.refresh()

        try:
            time.sleep(1)
        except KeyboardInterrupt:
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
    
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()
