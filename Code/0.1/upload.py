#! /usr/bin/python2

import time
import serial
import sys
import commands
import json
import shlex
import os


def serialize(s1, s2, s3):

    # Separate field values and their values
    f1 = shlex.split(s1)
    f2 = shlex.split(s2)
    f3 = shlex.split(s3)

    # Create JSON object
    feed = {}
    feed['version'] = '1.0.0'
    feed['datastreams'] = ({"id":f1[0], "current_value":f1[1]},\
            {"id":f2[0], "current_value":f2[1]},\
            {"id":f3[0], "current_value":f3[1]})


    # Write JSON object
    with open('feed_update.json', mode='w') as f:
        json.dump(feed, f, indent=4)


def upload(feed, key, feed_id):

    # Execute shell script for updating datastream
    os.system('./update.sh ' + feed + ' ' + key + ' ' + feed_id)


def main():

    # One argument is needed
    if len(sys.argv) is 1:
        print 'You must provide at least one argument.'
        sys.exit()

    filename = sys.argv[1]


    # Check if the serial interface exists
    try:
        with open(filename) as f: pass
    except IOError as e:
        print e, '\n'
        sys.exit()


    # Establish serial connection
    s = serial.Serial(filename, 9600)


    while 1:

        # Prevent from reading nonsense (fake reading)
        s_fake = s.readline()

        # Read different datastreams
        s1 = s.readline()
        s2 = s.readline()
        s3 = s.readline()

        # Encode data in JSON
        serialize(s1, s2, s3)

        # Upload data to Cosm
        upload('feed_update.json',\
                '0UUjNfQfxbqTirVhhVfQJdLlAlSSAKwzeHpJaTJtK2xPND0g',\
                '90291')

        # Sleep time
        time.sleep(30)




if __name__ == "__main__":
    main()
