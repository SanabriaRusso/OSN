#! /usr/bin/python2
# -*- coding: utf-8 -*-

# Import libraries
from argparse import ArgumentParser
import commands
import json
from serial import Serial
from serial import SerialException
from sys import exit
from time import sleep
from xbee import ZigBee
from ZBDispatch import ZBDispatch

def LM35(value):
    """ Convert analog value from the LM35
    temperature sensor to a proper temperature
    value, in Celsius.
    """

    return (value / 10.0)


def io_sample_handler(name, packet, debug):
    """
    Takes an incoming packet and extracts the useful
    information and creates a ready-to-serialize
    object (dict).

    Keyword arguments:
    name -- ID of the packet, i.e. 'rx_io_data_long_addr'
    packet -- The packet itself
    debug -- Wether content should be printed or not
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


def main():
    """
    After parsing arguments (-h flag for help), it instantiates an asynchronous dispatcher which creates a new thread for every packet that arrives.
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
        "io_data",
        io_sample_handler,
        lambda packet: packet['id']=='rx_io_data_long_addr',
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
