#! /usr/bin/python2


from xbee import ZigBee
import serial
import struct

PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

def hex(bindata):
    return ''.join('%02x' % ord(byte) for byte in bindata)

# Open serial port
ser = serial.Serial(PORT, BAUD_RATE)

# Create API object
xbee = ZigBee(ser,escaped=True)

# Continuously read and print packets
while True:
    try:
        response = xbee.wait_read_frame()
        print response
        sa = hex(response['source_addr_long'][4:])
        rf = hex(response['rf_data'])
        datalength=len(rf)
        # if datalength is compatible with two floats
        # then unpack the 4 byte chunks into floats
        if datalength==16:
            h=struct.unpack('f',response['rf_data'][0:4])[0]
            t=struct.unpack('f',response['rf_data'][4:])[0]
            #print sa,' ',rf,' t=',t,'h=',h
        # if it is not two floats show me what I received
        else:
	        print sa,' ',rf
    except KeyboardInterrupt:
        break

ser.close()
