from time import sleep

from mesh.linker import VirtualLink, UDPLink
from mesh.program import Switch, Printer
from mesh.filters import DuplicateFilter, StringFilter
from mesh.node import Node


ls = (UPDLink('en0', 2010), VirtualLink('vl1'), VirtualLink('vl2'), UDPLink('irc3', 2013), UPDLink('en4', 2014), UDPLink('irc5', 2013))
nodes = (
    Node('start', [ls[0]]),
    Node('l1', [ls[0], ls[2]], Program=Switch),
    Node('r1', [ls[0], ls[1]], Program=Switch),
    Node('l2', [ls[2], ls[3]], Program=Switch, Filters=(DuplicateFilter)),
    Node('r2', [ls[1], ls[4]], Program=Switch, Filters=(StringFilter.match(b'red'),) ),
    Node('end', [ls[4], ls[5]])
)

[l.start() for l in ls]
[n.start() for n in nodes]


if __name__ == "__main__":
    print("Using a mix of real and vitual links to make a little network...\n")
    print("          /[r1]<--vlan1-->[r2]<----vlan4---\\")
    print("[start]-en0                                [end]")
    print("          \[l1]<--vlan2-->[l2]<--irc3:irc5-/\n")


    print('\n', nodes)
    print("l2 wont forward two of the same packet in a row.")
    print("r2 wont forward any packet unless it contains the string 'red'.")
    print("Experiment by typing packets for [start] to send out, and seeing if they make it to the [end] node.")

    try:
        while True:
            print("------------------------------")
            message = input("[start]  OUT:".ljust(49))
            nodes[0].send(bytes(message, 'UTF-8'))
            sleep(1)
    except (EOFError, KeyboardInterrupt):   # CTRL-D, CTRL-C
        print(("All" if all([n.stop() for n in nodes]) else 'Not all') + " nodes stopped cleanly.")
        print(("All" if all([l.stop() for l in ls]) else 'Not all') + " links stopped cleanly.")
