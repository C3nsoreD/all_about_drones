"""
Echo server to handle socket connections
"""

import threading
import socketserver


class EchoRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # echo the data back to client
        data = self.request.recv(1024)
        cur_thread = threading.currentThread()
        response = b'%s: %s'% (cur_thread.getName().encode(), data)
        self.request.send(response)
        return

class ThreadedEchoServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    pass

if __name__ == "__main__":
    # Run socket server
    address = ('localhost', 9999)
    with ThreadedEchoServer(address, EchoRequestHandler) as server:
        ip, addr = server.server_address
        # t = threading.Thread(target = server.serve_forever)
        # t.setDaemon(True)
        # t.start()
        server.serve_forever()
        print(f"Using address {ip} : {addr} ")
        print(f"Server loop running in thread {t.getName()}")

 
