#!/usr/bin/python3
import sys,os,curses,json,time,select
from datetime import datetime
from collections import namedtuple
MemInfoEntry = namedtuple('MemInfoEntry', ['value', 'unit'])

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

    sysmemory.addstr(2, 2, 'MemFree  : ', curses.color_pair(1))
    sysmemory.addstr('{:.2f} GB'.format(float(meminfo['MemFree'].value)/1024/1024), curses.color_pair(4))

    mem_total = float(meminfo['MemTotal'].value)
    mem_percent = 100*(mem_total-float(meminfo['MemFree'].value))/mem_total

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

    result=os.statvfs('/var/lib/casper')
    block_size=result.f_frsize
    total_blocks=result.f_blocks
    free_blocks=result.f_bfree
    # giga=1024*1024*1024
    giga=1000*1000*1000
    total_size=total_blocks*block_size/giga
    free_size=free_blocks*block_size/giga
#    print('total_size = %s' % total_size)
#    print('free_size = %s' % free_size)

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
    validator.addstr('{:,} CSPR'.format(era_current_weight/1000000000, era_current_weight), curses.color_pair(4))

    validator.addstr(2, 2, 'ERA {}       : '.format(local_era+1), curses.color_pair(1))
    validator.addstr('{:,} CSPR'.format(era_future_weight/1000000000), curses.color_pair(4))

    validator.addstr(4, 2, 'Last Reward  : ', curses.color_pair(1))
    reward = era_future_weight - era_current_weight
    if (reward > 1000000000):
        validator.addstr('{:,} CSPR'.format(reward // 1000000000), curses.color_pair(4))
    else:
        validator.addstr('{:,} mote'.format(reward), curses.color_pair(4))


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
        system_memory()
        system_disk()

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
        sysmemory.refresh()
        sysdisk.refresh()
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
