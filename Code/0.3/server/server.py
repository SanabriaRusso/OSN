#! /usr/bin/python2
# -*- coding: utf-8 -*-

# Import libraries
from argparse import ArgumentParser
import commands
import json
from serial import Serial
from serial import SerialException
import struct
from sys import exit
from time import sleep
from xbee import ZigBee
from ZBDispatch import ZBDispatch


def hex(bindata):
    return ''.join('%02x' % ord(byte) for byte in bindata)

def direct_io_handler(name, packet, debug):
    """
    Takes an incoming packet and extracts the useful
    information and creates a ready-to-serialize
    object (dict). Used when XBee Direct I/O is enabled.

    Keyword arguments:
    name -- ID of the packet, i.e. 'rx_io_data_long_addr'
    packet -- The packet itself
    debug -- Wether the content should be printed or not
    """

    if debug:
        print "Samples Received: ", packet['samples']

    # Proper name of the samples
    proper_names = ['Temperature1',\
            'Temperature2',\
            ]

    # Will contain all datastreams and its values
    feed = {}
    feed['version'] = '0.2'
    feed['datastreams'] = ()

    # Form a valid JSON dictionary
    for i in range(0, (len(packet['samples']) + 1)):
        try:
            feed['datastreams'] = feed['datastreams'] + (\
                    {'id': proper_names[i],\
                    'current_value': str(LM35(packet['samples'][0].values()[i]))}\
                    ,)
        except IndexError as e:
            print "FATAL ERROR: ", e
            exit()

    # Write JSON object
    with open('feed.json', mode='w') as f:
        json.dump(feed, f, indent=4)

    # Upload information to Cosm
    commands.getstatusoutput('curl --request PUT --data-binary @feed.json --header "X-ApiKey: aTh_eoPhHeK9yJVjz4wJMXIh1kiSAKxrTGZPM2tUWHJ3TT0g" --verbose http://api.cosm.com/v2/feeds/98160')


def xbee_arduino_handler(name, packet, debug):
    """
    Takes an incoming packet and extracts the useful
    information and creates a ready-to-serialize
    object (dict). The packets come from an Arduino
    with a XBee module attached.

    Keyword arguments:
    name -- ID of the packet, i.e. 'rx'
    packet -- The packet itself
    debug -- Wether the content should be printed or not
    """

    if debug:
        print packet

    sa = hex(packet['source_addr_long'][4:])
    rf = hex(packet['rf_data'])
    datalength=len(rf)
    # if datalength is compatible with two floats
    # then unpack the 4 byte chunks into floats
    print datalength
    if datalength==24:
        h=struct.unpack('f',packet['rf_data'][0:4])[0]
        t=struct.unpack('f',packet['rf_data'][4:8])[0]
        s=struct.unpack('f',packet['rf_data'][8:])[0]
        print sa,' ',rf,' t=',t,'h=',h,'s=',s

    else:
        print sa,' ',rf


def main():
    """
    After parsing arguments , it instantiates an asynchronous dispatcher which creates a new thread for every packet that arrives.
    """

    # Argument parsing
    parser = ArgumentParser(description='Receives data from any number or XBee routers in API mode using Direct I/O and then uploads this information to Cosm.')
    parser.add_argument('--debug', help='prints everything that the coordinator receives', action='store_true', default=False)
    parser.add_argument('device_file', help='where the zigbee cordinator is connected', action='store')
    parser.add_argument('baud_rate', action='store', type=int)
    args = vars(parser.parse_args())


    # Serial connection with the XBee
    try:
        ser = Serial(args['device_file'], args['baud_rate'])
    except SerialException as s:
        print s
        exit()
    print "Listening on", args['device_file'], "...\n"


    # Asynchronous dispatcher
    dispatch = ZBDispatch(ser)
    dispatch.register(
        "direct_io",
        direct_io_handler,
        lambda packet: packet['id']=='rx_io_data_long_addr',
        args['debug']
    )
    dispatch.register(
        "io_data",
        xbee_arduino_handler,
        lambda packet: packet['id']=='rx',
        args['debug']
    )
    zb = ZigBee(ser, callback=dispatch.dispatch)


    # Main loop
    while True:
        try:
            sleep(.1)
        except KeyboardInterrupt as k:
            print k
            break


    # Close XBee connection
    zb.halt()
    ser.close()


if __name__ == "__main__":
    main()
