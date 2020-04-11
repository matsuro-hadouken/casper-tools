#!/bin/bash


# REQUIREMENTS:

# 'node, npm''

# 'npm install log-color-highlight -g'

# 'sudo apt install jq'

# color   Highlighting color, style, preset or modifier. Allowed values:
#                Colors: black red green yellow blue magenta cyan white gray
#                Background colors: bgBlack bgRed bgGreen bgYellow bgBlue bgMagenta bgCyan bgWhite
#                Styles: reset bold dim italic underline inverse hidden strikethrough
#                Presets: any preset defined with '-p' parameter

LOG_PATH='/home/casper/.casperlabs/log.0.txt'

HANDLING='Handling incoming message='
UNCAUGHT='Uncaught Exception :'
FINISHED='Finished handling incoming message='
ATTEMPTING='Attempting to add is_booking_block='
ADD_MESSAGE='Added message='
PEER_SIZE='Peers: size='
EXE='Executing action='
CREATE='Created kind='
F_CREATE='Finished handling created message='
SCHEDULE='Scheduling action='
ERROR='error'

tail -f $LOG_PATH |  jq '.text | .message | select (.!=null)' | lch -red.wl "$UNCAUGHT" "$ERROR" -yellow.wl "$HANDLING" "$ATTEMPTING" -green.wl "$FINISHED" "$ADD_MESSAGE" -cyan.wl "$PEER_SIZE" "$F_CREATE" -magenta.wl "$EXE" "$CREATE" "$SCHEDULE"



