# Code files

The code here is mainly written in Python and C/C++ (for Arduino). 

You'll need the *python-xbee* library so the with an XBee can be established in API mode. Here is a little description of what you'll find in each subdirectory:

* 0.1 -- An Arduino with an XBee module attached to it transmits in transparent mode to an XBee in coordinator AT mode plugged into a server.
* 0.2 -- A standalone XBee works in API mode gathering data from an analogic sensor and then a server running a script uploads the information to Cosm.
* 0.3 -- The Arduino can now transmit with an XBee in API mode and the server receives/parses the data and uploads it to the Internet, as well from a standalone XBee.
* Utils -- Here there are the libraries as well as some useful scripts I found, as *SConstruct*, used to upload data to the Arduino through the terminal under GNU/Linux.

**NOTE:** You must change the API keys from Cosm, they're just a former example and they don't work anymore.
