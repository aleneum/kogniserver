#!/bin/bash

export PYTHONPATH="$PYTHONPATH:/Users/alneuman/kognihome/rsb-wamp-bridge/env/lib/python2.7/site-packages"
echo booting router...
/Users/alneuman/kognihome/rsb-wamp-bridge/env/bin/crossbar start --cbdir /Users/alneuman/kognihome/rsb-wamp-bridge/env/etc/crossbar &
# give the router some time to boot
sleep 5
echo booting rsb bridge...
/Users/alneuman/kognihome/rsb-wamp-bridge/env/bin/asyncio-rsb-bridge

# bash magic http://stackoverflow.com/questions/360201/kill-background-process-when-shell-script-exit
# trap 'traps' kill signals, then deregisters SIGTERM to not loop infinitely and then kills all processes
# with PID of the script (all detached processes)
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
