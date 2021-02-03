import random
from data import Data


class Node:
    """
     A node represents a drone in the network, the drone is connected to other drones via links
     the drone receives data and processes it according to the data's header;
    """
    def __init__(self, name="d1", interfaces=None):
        """
         A drone can join the network through collecting a list of other drones in the network through the interfaces object.
        """
        self.name = name
        # the interfaces object can be populated or empty
        self.interfaces = interfaces or []
        self.ID = self._generate_ID()

    @staticmethod
    def _generate_ID(sel, charset='abcdef0987654321', segment=9, segment_len=3, delimiter='-'):
        """
         Generates a non-qunique ID similar to mac
        """
        addr = []
        for _ in range(segment):
            sub  = ''.join(random.choice(charset) for _ in range(segment_len))
            addr.append(sub)
        return delimiter.join(addr)
