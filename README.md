 - Auction tool, show data related to bonds and bids
``` bash
active_validators.sh <CAN_ACCEPT_PUB_HEX if empty parse from $public_hex_path by default>
```
 - check HEX balance
 ``` bash
balance_check.sh <PUB_HEX>
```
 - deploy bonding transaction ( _example, watch gas !_ )
 ``` bash
bond.sh
```
 - connected peers explorer
 ``` bash
explorer.sh
```
 - active node status (python script) (press ctrl-c to exit)
 ``` bash
status.py
```
![alt text](https://github.com/RapidMark/casper-tools/raw/master/images/status.PNG)
 - delegation tool, allow user to stake
```
delegate.sh
```
 - delegation tool, allow user to withdraw stake
```
undelegate.sh
```
- validator tool, allow validator to withdraw from auction
```
withdraw_bid.sh
```
