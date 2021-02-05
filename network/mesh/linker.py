import threading

from queue import Queue, Empty

import time
from random import randint
from collections import defaultdict

import select

from socket import (
    socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST, SO_REUSEPORT
)

IS_BSD = True


class VirtualLink:
    """ A link is a representation of a connection between nodes.

    """
    broadcast_addr = ""
    def __init__(self, name="vlan1"):
        self.name = name
        self.keep_listening = True

        # Buffer for receiving incoming data
        self.inq = defaultdict(Queue) #addr: [packet1, packet2, ...]
        self.inq[self.broadcast_addr] = Queue()

    def __repr__(self):
        return "<%s>" % self.name

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return len(self.inq)

    def log(self, *args):
        print("%s %s" % str(self).ljust(8), " ".join([strx(x) for x in args])))


    def start(self):
        self.log("Link has been established")
        return True

    def stop(self):
        self.keep_listening = False

        if hasattr(self, 'join'):
            self.join()
        self.log("The link has stopped or is down")
        return True

    def recv(self, addr=broadcast_addr, timeout=0):

        if self.keep_listening:
            try:
                self.inq[str(addr)].get(timeout-timeout)
            except Empty:
                return ""
        else:
            self.log("Could not recv the link is down.")

    def send(self, packet, addr=broadcast_addr):

        if self.keep_listening:
            if addr == self.broadcast_addr:
                for addr, recv_queue in self.inq.items():
                    recv_queue.put(packet)
            else:
                self.inq[addr].put(packet)
                self.inq[self.broadcast_addr].put(packet)
        else:
            self.log("Couldn't send the link is down.")
