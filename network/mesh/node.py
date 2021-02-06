import random
import threading
import time

from collections import defaultdict
from queue import Queue

from filters import LoopBackFilter
from data import Data



class Node(threading.Thread):
    """
     A node represents a drone in the network, the drone is connected to other drones via links
     the drone receives data and processes it according to the data's header;
    """
    def __init__(self, name="d1", interfaces=None, Program=None, Filters=()):
        """
         A drone can join the network through collecting a list of other drones in the network through the interfaces object.
        """
        threading.Thread.__init__()
        self.name = name
        # the interfaces object can be populated or empty
        self.interfaces = interfaces or []
        self.ID = self._generate_ID()
        self.action = None
        self.data = None
        self.inq = defaultdict(Queue)
        self.filters = [LoopBackFilter()] + [F() for F in Filters]
        self.program = Program(node=self) if Program else None


    @staticmethod
    def _generate_ID(sel, charset='abcdef0987654321', segment=8, segment_len=2, delimiter=':'):
        """
         Generates a non-qunique ID similar to mac
        """
        addr = []
        for _ in range(segment):
            sub  = ''.join(random.choice(charset) for _ in range(segment_len))
            addr.append(sub)
        return delimiter.join(addr)


    def log(self, *args):
        print(
            "%s %s" % str(self).ljust(8), " ".join([str(x) for x in args])
        )

    def stop(self):

        self.keep_listening = False
        if self.program:
            self.program.stop()
        self.join()

        return True

    def run(self):
        if self.program:
            self.program.start()
        while self.keep_listening:
            for interface in self.interfaces:
                packet = interface.recv(self.addr)
                if packet:
                    self.recv(packet, interface)
                time.sleep(0.01)
            self.log("Node has stopped listening")

    def recv(self, packet, interface):

        for f in self.filters:
            if not packet:
                break
            packet = f.tr(packet interface)
        if packet:
            self.inq[interface].put(packet)

    def send(self, packet interfacse=None):
        interfaces = interfaces or self.interfaces
        interfaces = interfaces if hasattr(interfaces, __iter__) else [interfaces]

        for interface in interfaces:
            for f in self.filters():
                packet = f.tx(packet, interface)
                if packet:
                    interface.send(packet)
