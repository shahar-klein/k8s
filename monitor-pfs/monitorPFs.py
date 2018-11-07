#!/usr/bin/python

import sys
import argparse
import signal
import threading
import time
from threading import Thread
import Queue
from pyroute2 import IPDB
from pyroute2 import IPRoute

work_queue = Queue.Queue()
ip = IPDB()
ipr = IPRoute()


def link_state_cb(ipdb, msg, action):
    if action == 'RTM_NEWLINK':
        work_queue.put(msg)

def handler(signum, frame):
    print "\nShutting down."
    ip.release()

def getNumVFs(dev):
    sysf="/sys/class/net/%s/device/sriov_numvfs" % dev
    f = open(sysf, 'r')
    numvfs = f.read()
    return int(numvfs)

class PF:
    def __init__(self, name, state, numvfs):
        self.name = name
        self.state = state
        self.numvfs = numvfs
        self.reps = []
        for i in range(0, self.numvfs):
            self.reps.append("%s_%d" % (self.name, i))

    def setRepsState(self):
        for rep in self.reps:
            print "Setting:", rep, self.state
            if self.state == 1:
                state='up'
            else:
                state = 'down'
            ipr.link('set', index=ipr.link_lookup(ifname=rep)[0], state=state)

class MonitorPFs(Thread):
    def setPFs(self, pfs):
        self.pfs = {}
        for pf in pfs:
            numvfs = getNumVFs(pf)
            ix = ipr.link_lookup(ifname=pf)
            dev = ipr.get_links(ix)
            state = dev[0].get_attr('IFLA_CARRIER', '')
            self.pfs[pf] = PF(pf, state, numvfs)

        #print self.pfs[pf].numvfs

    def run(self):
        while True:
            msg = work_queue.get()
            ifname = msg['attrs'][0][1]
            if ifname in self.pfs.keys():
                print "Got msg about: " , ifname
                newState = msg.get_attr('IFLA_CARRIER', '')
                if newState != self.pfs[ifname].state:
                    self.pfs[ifname].state = newState
                    self.pfs[ifname].setRepsState()

class Config:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--pfs", nargs='+', help="Space separated list of PFs to monitor", type=str)
        args = parser.parse_args()
        self.pfs = args.pfs

def main():

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    c = Config()
    mpfs = MonitorPFs()
    mpfs.setPFs(c.pfs)
    mpfs.daemon = True
    mpfs.start()

    ip.register_callback(link_state_cb)

    signal.pause()

if __name__ == "__main__":

    main()

