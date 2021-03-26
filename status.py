#!/usr/bin/python3
import sys,os,curses,json,time,select
from datetime import datetime

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
    block_info = curses.newwin(13, 70, 7, 0)
    block_info.box()
    box_height, box_width = block_info.getmaxyx()
    text_width = box_width - 17 # length of the Text before it gets printed
    block_info.addstr(0, 2, 'Casper Block Info', curses.color_pair(4))

    try:
        global_status = json.loads(os.popen('curl -s 31.7.207.16:8888/status | jq -r .last_added_block_info').read())
        global_height = global_status['height']
    except:
        global_height = 'null'

    global local_status
    local_status = json.loads(os.popen('curl -s localhost:8888/status').read())
    try:
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


    index = 1
    block_info.addstr(index, 2, 'Local height : ', curses.color_pair(1))
    block_info.addstr('{}'.format(local_height), curses.color_pair(4))

    index += 1
    block_info.addstr(index, 2, 'Chain height : ', curses.color_pair(1))
    block_info.addstr('{}'.format(global_height), curses.color_pair(4))
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

def casper_public_key():
    global pub_key_win
    pub_key_win = curses.newwin(3, 70, 20, 0)
    pub_key_win.box()
    box_height, box_width = pub_key_win.getmaxyx()
    text_width = box_width - 17 # length of the Text before it gets printed
    pub_key_win.addstr(0, 2, 'Public Key', curses.color_pair(4))

    pub_key_win.addstr(1, 2, '{}'.format(public_key), curses.color_pair(1))


def casper_validator():
    global validator
    validator = curses.newwin(6, 70, 23, 0)
    validator.box()
    box_height, box_width = validator.getmaxyx()
    text_width = box_width - 17 # length of the Text before it gets printed
    validator.addstr(0, 2, 'Casper Validator Info', curses.color_pair(4))

    try:
        last_added_block_info = local_status['last_added_block_info']

        try:
            local_era = last_added_block_info['era_id']
        except:
            local_era = 0
    except:
        local_era = 0

    try:
        era_current_weight = json.loads(os.popen('casper-client get-auction-info | jq -r \'.result.auction_state.era_validators | .[0].validator_weights[] | select(.public_key=="{}")| .weight\''.format(public_key)).read())
        era_future_weight  = json.loads(os.popen('casper-client get-auction-info | jq -r \'.result.auction_state.era_validators | .[1].validator_weights[] | select(.public_key=="{}")| .weight\''.format(public_key)).read())
    except:
        era_current_weight = 0;
        era_future_weight = 0;

    validator.addstr(1, 2, 'ERA {}       : '.format(local_era), curses.color_pair(1))
    validator.addstr('{:,} CSPR'.format(era_current_weight/1000000000, era_current_weight), curses.color_pair(4))

    validator.addstr(2, 2, 'ERA {}       : '.format(local_era+1), curses.color_pair(1))
    validator.addstr('{:,} CSPR'.format(era_future_weight/1000000000), curses.color_pair(4))

    validator.addstr(4, 2, 'Last Reward  : ', curses.color_pair(1))
    reward = era_future_weight - era_current_weight
    if (reward > 1000000000):
        reward //=1000000000
    validator.addstr('{:,}'.format(reward), curses.color_pair(4))


def draw_menu(casper):
    k = 0
    cursor_x = 0
    cursor_y = 0

    # Clear and refresh the screen for a blank canvas
    casper.clear()
    casper.refresh()

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
        height, width = casper.getmaxyx()

        cursor_x = width-1
        cursor_y = height-1

        casper_launcher()
        casper_block_info()
        casper_public_key()
        casper_validator()

        # Render status bar
        statusbarstr = "Press 'ctrl-c' to exit | STATUS BAR "
        casper.attron(curses.color_pair(3))
        casper.addstr(height-1, 1, statusbarstr)
        casper.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        casper.attroff(curses.color_pair(3))

        # Refresh the screen

        launcher.refresh()
        block_info.refresh()
        pub_key_win.refresh()
        validator.refresh()
        casper.refresh()

        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break;

        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            k = casper.getch()

def main():
    os.environ['NCURSES_NO_UTF8_ACS'] = '1'
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()
