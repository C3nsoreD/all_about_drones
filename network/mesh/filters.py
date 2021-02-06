from collections import defaultdict
import random


class BaseFilter:
    """ Implements a filter, which is used by a node on incoming data.
        Each filter has receive and send `tr, tx` class method.
    """
    @classmethod
    def tr(self, packet, interface):
        return packet

    @classmethod
    def tx(self, packet, interface):
        return packet


class DuplicateFilter(BaseFilter):
    """ Filter that creates duplicates of each request.

    """

    def __init__(self):
        # Create duplicate packets for recv and send
        self.last_sent = defaultdict(str)
        self.last_recv = defaultdict(str)


    def tr(self, packet, interface):
        """
        """
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
            return None
        else:
            self.sent_hashes[hash(packet)] += 1
            return packet
