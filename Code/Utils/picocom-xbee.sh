#!/usr/bin/env bash
#
# Provide just a single argument, being the device file.
#
# USAGE:
# picocom_xbee /dev/ttyUSB0
#

if [ -z "$1" ]
then
        echo "Device file not defined."
else
        picocom --echo --imap crcrlf $1
fi
