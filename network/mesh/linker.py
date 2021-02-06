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
        print("%s %s" % str(self).ljust(8), " ".join([strx(x) for x in args]))


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


class UDPLink(threading.Thread, VirtualLink):

    def __init__(self, name="en0", port=2020):
        threading.Thread.__init__(self)
        VirtualLink.__init__(self, name=name)
        self.port = port

        self._initsocket()

    def __repr__(self):
        return "< %s >" % self.name

    def _initsocket(self):
        """ creates send and recv sockets with broadcast options.
            sockets are set non blocking to prevent deadlocks.

        """

        self.send_socket = socket(AF_INET, SOCK_DGRAM)
        self.send_socket.setblocking(0)
        self.send_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        self.recv_socket = socket(AF_INET, SOCK_DGRAM)
        self.recv_socket.setbloackng(0)

        self.recv_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.recv_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.recv_socket.bind(('', port))


    def run(self):

        while self.keep_listening:
            try:
                read_ready, w, x = select.select([self.recv_socket], [], [], 0.01)
            except Exception:
                pass

            if read_ready:
                packet, addr = read_ready[0].recvfrom(4096)
                if addr[1] == self.port:
                    for addr, recv_queue in self.inq.items():
                        recv_queue.put(packet)
                else:
                    pass


    def send(self, packet, retry=True):
        addr = ('255.255.255.255', self.port)
        try:
            self.send_socket.sendto(packet, addr)
        except Exception as e:
            self.log("Line failed to send over socket %s" % e)
            sleep(0.2)

            if retry:
                self.send(packet, retry=False)
