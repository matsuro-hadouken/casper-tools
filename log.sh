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
ERA_CREATED='Created era='

LFB='New last finalized block'

ERROR='error'

VOTE='vote any main child'

APPROVAL='Added new approval'

METRIX_REPORT='Reporting metrics to destination='

STARTING="Starting node"

LISTENING="Listening"

REQUIRED='reached required min_successful'

tail -f $LOG_PATH |  jq '.text | .message | select (.!=null)' | lch -red.wl "$UNCAUGHT" "$ERROR" "$VOTE" "$REQUIRED"  -yellow.wl "$HANDLING" -white.bold.wl "$ATTEMPTING" -green.wl "$LISTENING"  "$FINISHED" "$APPROVAL" "$METRIX_REPORT"  "$ADD_MESSAGE" -cyan.wl "$PEER_SIZE" "$F_CREATE" -magenta.wl "$EXE" "$CREATE" "$STARTING" "$SCHEDULE" "$LFB" -red.bold "$ERA_CREATED" 
