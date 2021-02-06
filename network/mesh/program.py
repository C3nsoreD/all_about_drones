import threading

from mesh.router import Router


class BaseProgram(threading.Thread):
    def __init__(self, node):
        threading.Thread.__init__(self)
        self.keep_listening = True
        self.node = node

    def run(self):
        while self.keep_listening:
            for interface in self.node.interfaces:
                try:
                    #
                    self.recv(self.node.inq[interface].get(timeout=0), interface)
                except Empty:
                    sleep(0.01)

    def stop(self):
        self.keep_listening = False
        self.join()

    def recv(self, packet, interface):
        # Method will be overloaded to handle recieved data
        pass


class RouteProgram(BaseProgram):

    router = Router()

    def __init__(self, node):
        super(RouteProgram, self).__init__(node)
        self.router.node = node

    def recv(self, packet, interface):
        message = packet.decode()
        # log message
        # call routers recv object
        self.router.recv(self, message, interface)

    def send(self):
        if not (hasattr(message, __iter__) and not hasattr(message, __iter__)):
            message = [message]

        for line in message:
            line = line if type(line) in (str, bytes) else '{0}'.format(line)
            if not line.strip():
                continue

            packet = bytes(line, 'utf-8') if type(line) is str else line
            self.node.send(packet, interface)


class Switch(BaseProgram):
    def recv(self, packet, interface):
        other_interfaces = set(self.node.interfaces) - {interface}
        if packet and other_interfaces:
            self.node.log("SWITCH " + (str(interface) + ">>>> <" + "".join(i.name for i in other_interfaces)+">").ljust(30), packet.decode())
            self.node.send(packet, interfaces=other_interfaces)


class Printer(BaseProgram):
    def recv(self, packet, interface):
        sleep(0.2)
        self.node.log(("\nPRINTER: %s" % interface).ljust(30), packet.decode())
