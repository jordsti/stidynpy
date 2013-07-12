import urllib2
import hashlib
import os
import time

ip_url = "http://stinetwork.info/ip.php"
config_file = "config.dyn"

class DynWatcher:
    def __init__(self):
        self.config = ConfigFile(config_file)
        self.config.readfile()
        self.freedns = FreeDNSSupport()

        self.interval = self.config.time
        self.domains = self.config.domains
        self.last_ip = getPublicIP()
        self.dyndoms = []


    
    def matchdomains(self, entry):

        for d in self.domains:
            if d == entry.domain:
                return True

        return False


    def loop(self):
        print "Starting DynWatcher..."

        if len(self.domains) == 0:
            print "No domain are listed for verification..."
            print "Quitting"
            return

        while True:
            self.dyndoms = self.freedns.get_domains(self.config.key)
            self.last_ip = getPublicIP()

            print "Your ip is "+self.last_ip

            for dyn in self.dyndoms:
                if self.matchdomains(dyn):
                    if dyn.current_ip != self.last_ip:
                        print dyn.domain+" IP is "+dyn.current_ip+" need update !"
                        dyn.update()
                    else:
                        print dyn.domain+" is up-to-date"

            print "Sleeping..."
            time.sleep(self.interval)

    

class ConfigFile:
    def __init__(self, fpath):
        self.fpath = fpath
        self.key = ""
        self.domains = []
        self.time = 300


    def readfile(self):
        if os.path.exists(self.fpath):
            fp = open(self.fpath, 'r')

            line = fp.readline()

            while len(line) != 0:
                if not line.startswith("#"):
                    line = line.rstrip("\n")
                    if line.startswith("key:"):
                        self.key = line.lstrip("key:")
                    elif line.startswith("time:"):
                        self.time = int(line.lstrip("time:"))
                    else:
                        self.domains.append(line)

                line = fp.readline()

            fp.close()

class DynDNSEntry:

    def __init__(self, stringdata):
        self.domain = ""
        self.current_ip = ""
        self.update_url = ""

        data = stringdata.split("|")
        ld = len(data)

        if data >= 1:
            self.domain = data[0]
        if data >= 2:
            self.current_ip = data[1]
        if data >= 3:
            self.update_url = data[2]

    def update(self):
        if len(self.update_url) != 0:
            req = urllib2.urlopen(self.update_url)
            print req.read()

class FreeDNSSupport:

    def __init__(self):
        self.domains_url = "http://freedns.afraid.org/api/?action=getdyndns&sha="

    def gen_config_file(self, user, password):
        key = self.get_key(user, password)
        doms = self.get_domains(key)

        fp = open(config_file, "w")

        fp.write("#Auto-generated file for stidynpy \n")
        fp.write("#Line starting with # are ignored !\n")
        fp.write("# important ! starting with your afraid key sha1(user|password) \n")
        fp.write("#key:hexadecimal string \n")
        fp.write("#\n")
        fp.write("#\n")
        fp.write("#------- YOUR KEY --------------\n")
        fp.write("key:"+key+"\n")
        fp.write("#------- YOUR KEY --------------\n")
        fp.write("#\n")
        fp.write("#\n")
        fp.write("#All your domains are listed here, remove # to uncomment the line\n")
        fp.write("#-------- DOMAINS SECTION ---------\n")


        for d in doms:
            fp.write("#"+d.domain+"\n")
        fp.write("#-------- DOMAINS SECTION ---------\n")
        fp.write("#\n")
        fp.write("#\n")
        fp.write("#\n")
        fp.write("#-------- WATCHER PARAMETER ------- \n")
        fp.write("# time: time in seconds before the next check \n")
        fp.write("time:300\n")
        fp.write("#-------- WATCHER PARAMETER ------- \n")
        fp.write("#End")
        fp.close()
        
    def get_key(self, user, password):
        sha = hashlib.sha1()
        sha.update(user + "|" + password)
        shastr = sha.hexdigest()
        return shastr
    
            
    def get_domains(self, key):
        url = self.domains_url + key
        req = urllib2.urlopen(url)
        domains = req.read()

        dnsentries = []
        
        domains = domains.split("\n")
        for dom in domains:
            dnsentries.append(DynDNSEntry(dom))

        return dnsentries      


def getPublicIP():
    return getUrl(ip_url)
    
def getUrl(url):
    try:
        req = urllib2.urlopen(url)
        data = req.read()
    except:
        print "Cannot get the url"
        return "ERROR"
    return data

#Create a config file on the first run
def create_config_file():
    print "FreeDNS Dynamic DNS configuration"
    print "Enter your username and password, they will be hashed to generate your key"
    user = raw_input("username :").rstrip("\n")
    password = raw_input("password :").rstrip("\n")
    fdns = FreeDNSSupport()
    print "Now querying afraid.org to generate a config file..."
    fdns.gen_config_file(user, password)
    print "Config file generated, please edit config.dyn"

import sys
#main entry point
if __name__ == "__main__":
    argc = len(sys.argv)

    if argc == 1:
        #no param
        if os.path.exists(config_file):
            #starting the watcher
            watcher = DynWatcher()
            watcher.loop()
        else:
            print "Config file doesn't exists !"
            create_config_file()
    else:
        print "Parameters not handled at this moment!"




