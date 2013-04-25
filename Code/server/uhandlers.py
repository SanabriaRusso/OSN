#! /usr/bin/python2

def cosm_upload(sa, data):
    """
    Uploads gathered data to the Internet given a source address and a list with different values.
    """

    # Will contain all datastreams and its values
    feed = {}
    feed['version'] = '0.3'
    feed['datastreams'] = ()


    # Form a valid JSON dictionary
    for i in range(0, len(data)):
        try:
            feed['datastreams'] = feed['datastreams'] + (\
                    {'id': str(i),\
                    'current_value': str(data[i])\
                    }\
                    ,)
        except IndexError as e:
            print "ERROR: ", e
            exit()


    # Write JSON object
    with open('feed.json', mode='w') as f:
        json.dump(feed, f, indent=4)


    try:
        addr_file = open('addr.pck', 'r')
        addr = pickle.load(addr_file)

        if not addr.has_key(sa):
            addr_file.close()
            addr_file = open('addr.pck', 'w')

            # ------ FEED CREATION ------ #
            new_feed = {}
            new_feed['title'] = sa
            new_feed['version'] = '0.3'
            with open('new_feed.json', mode='w') as f:
                json.dump(new_feed, f, indent=4)
            o = commands.getstatusoutput('curl --request POST --data-binary @new_feed.json --header "X-ApiKey: yXt35WoQD-LyLj7aK7kGVEkZI-KSAKxOMTNpRXVDdTNhWT0g" --verbose http://api.cosm.com/v2/feeds/')
            try:
                url = re.search('http://api.cosm.com/v2/feeds/\d+', o[1]).group()
            except AttributeError as att:
                print att

            addr[sa] = url
            pickle.dump(addr, addr_file)

            # ------ DATA UPLOAD ------ #
            out = commands.getstatusoutput('curl --request PUT --data-binary @feed.json --header "X-ApiKey: yXt35WoQD-LyLj7aK7kGVEkZI-KSAKxOMTNpRXVDdTNhWT0g" --verbose ' + addr[sa])

        else:
            # ------ DATA UPLOAD ------ #
            out = commands.getstatusoutput('curl --request PUT --data-binary @feed.json --header "X-ApiKey: yXt35WoQD-LyLj7aK7kGVEkZI-KSAKxOMTNpRXVDdTNhWT0g" --verbose ' + addr[sa])
            #print out[1]

    except EOFError:
        addr_file = open('addr.pck', 'w')
        pickle.dump({}, addr_file)
    except IOError:
        print 'WARNING: There is no addresses file, creating a new one...'
        addr_file = open('addr.pck', 'w')
        pickle.dump({}, addr_file)
    finally:
        addr_file.close()
