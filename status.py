#!/usr/bin/python3
import sys,os,curses,json,time,select

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

    public_key=os.popen('curl -s localhost:8888/status | jq -r .our_public_signing_key').read().split('\n')[0]

    # Loop where k is the last character pressed
    while (k != ord('q')):

        # Initialization
#        casper.clear()
        height, width = casper.getmaxyx()

        casper.border(0)
        casper.addstr(0, 2, 'Casper Node Monitor', curses.color_pair(4))

        cursor_x = width-1
        cursor_y = height-1

        index = 1;

        key_value = os.popen('systemctl show casper-node-launcher.service | grep -e MemoryCurrent -e ActiveState -e LoadState -e FragmentPath -e StateChangeTimestamp=').read().split('\n')
        json_dict = {}
        for entry in key_value:
            kv = entry.split("=", 1)
            if len(kv) == 2:
                json_dict[kv[0]] = kv[1]

        casper.addstr(index, 1, 'MemoryCurrent: ', curses.color_pair(1))
        casper.addstr('{}'.format(json_dict['MemoryCurrent']), curses.color_pair(4))
        index += 1
        casper.addstr(index, 1, 'ActiveState  : ', curses.color_pair(1))
        casper.addstr('{}'.format(json_dict['ActiveState']), curses.color_pair(4))
        index += 1
        casper.addstr(index, 1, 'LoadState    : ', curses.color_pair(1))
        casper.addstr('{}'.format(json_dict['LoadState']), curses.color_pair(4))
        index += 1
        casper.addstr(index, 1, 'FragmentPath : ', curses.color_pair(1))
        casper.addstr('{}'.format(json_dict['FragmentPath']), curses.color_pair(4))
        index += 1
        casper.addstr(index, 1, 'Timestamp    : ', curses.color_pair(1))
        casper.addstr('{}'.format(json_dict['StateChangeTimestamp']), curses.color_pair(4))
        index += 1


        index += 1
        casper.addstr(index, 1, 'Public Key   : ', curses.color_pair(1))
        casper.addstr('{}'.format(public_key), curses.color_pair(4))
        index += 1

        try:
            global_status = json.loads(os.popen('curl -s 31.7.207.16:8888/status | jq -r .last_added_block_info').read())
            global_height = global_status['height']
        except:
            global_height = 'null'

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


        try:
            era_current_weight = json.loads(os.popen('casper-client get-auction-info | jq -r \'.result.auction_state.era_validators | .[0].validator_weights[] | select(.public_key=="{}")| .weight\''.format(public_key)).read())
            era_future_weight  = json.loads(os.popen('casper-client get-auction-info | jq -r \'.result.auction_state.era_validators | .[1].validator_weights[] | select(.public_key=="{}")| .weight\''.format(public_key)).read())
        except:
            era_current_weight = 0;
            era_future_weight = 0;

        index += 1
        casper.addstr(index, 1, 'Local height : ', curses.color_pair(1))
        casper.addstr('{}'.format(local_height), curses.color_pair(4))

        index += 1
        casper.addstr(index, 1, 'Chain height : ', curses.color_pair(1))
        casper.addstr('{}'.format(global_height), curses.color_pair(4))
        index += 1
        casper.addstr(index, 1, 'Round Length : ', curses.color_pair(1))
        casper.addstr('{}'.format(round_length), curses.color_pair(4))
        index += 1
        casper.addstr(index, 1, 'Next Upgrade : ', curses.color_pair(1))
        casper.addstr('{}'.format(next_upgrade), curses.color_pair(4))
        index += 1
        casper.addstr(index, 1, 'Build Version: ', curses.color_pair(1))
        casper.addstr('{}'.format(build_version), curses.color_pair(4))

        index += 2
        casper.addstr(index, 1, 'Chain Name   : ', curses.color_pair(1))
        casper.addstr('{}'.format(chain_name), curses.color_pair(4))
        index += 1
        casper.addstr(index, 1, 'Starting Hash: ', curses.color_pair(1))
        casper.addstr('{}'.format(root_hash), curses.color_pair(4))

        index += 2
        casper.addstr(index, 1, 'API Version  : ', curses.color_pair(1))
        casper.addstr('{}'.format(api_version), curses.color_pair(4))
        index += 1
        casper.addstr(index, 1, 'Local ERA    : ', curses.color_pair(1))
        casper.addstr('{}'.format(local_era), curses.color_pair(4))

        index += 2
        casper.addstr(index, 1, 'ERA {}       : '.format(local_era), curses.color_pair(1))
        casper.addstr('{}'.format(era_current_weight), curses.color_pair(4))
        index += 1
        casper.addstr(index, 1, 'ERA {}       : '.format(local_era+1), curses.color_pair(1))
        casper.addstr('{}'.format(era_future_weight), curses.color_pair(4))
        index += 1
        casper.addstr(index, 1, 'Last Reward  : ', curses.color_pair(1))
        casper.addstr('{}'.format(era_future_weight - era_current_weight), curses.color_pair(4))

        # Render status bar
        statusbarstr = "Press 'ctrl-c' to exit | STATUS BAR "
        casper.attron(curses.color_pair(3))
        casper.addstr(height-1, 1, statusbarstr)
        casper.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        casper.attroff(curses.color_pair(3))

        # Refresh the screen
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
