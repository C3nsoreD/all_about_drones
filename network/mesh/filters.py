from collections import defaultdict
import random


class BaseFilter:

    @classmethod
    def tr(self, packet, interface):
        return packet

    @classmethod
    def tx(self, packet, interface):
        return packet



class DuplicateFilter(BaseFilter):
    def __init__(self):
        self.last_sent = defaultdict(str)
        self.last_recv = defaultdict(str)


    def tr(self, packet, interface):
        if not packet or packet == self.last_recv[interface]:
            return None
        else:
            self.last_recv[interface] = packet
            return packet

    def tx(self, packet, interface):
        if not packet or packet == self.last_sent[interface]:
            return None
        else:
            self.last_sent[interface] = packet
            return packet


class LoopBackFilter(BaseFilter):
    def __init__(self):
        self.sent_hashes = defaultdict(int)


    def tr(self, packet, interface):
        if not packet:
            return None
        elif self.sent_hashes[hash(packet)] > 0:
            self.sent_hashes[hash(packet)] -= 1
            return None
        else:
            return packet

    def tx(self, packet, interface):
        if not packet:
            return None:
        else:
            self.sent_hashes[hash(packet)] += 1
            return packet
