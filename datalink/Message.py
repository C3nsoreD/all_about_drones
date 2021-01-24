#!/usr/bin/env python3

"""
    Message: data object used to send and receive data between drones and server
"""
import sys
import io
import struct
import json
import selectors

# The message:
#   Representation information sent from the drone to the server and vice versa
#   the message contains agregated data from collected from the sensors.
#   Data sent though sockets is sent as bytes thus, it to be converted.
###
#   For the simulation, random text will represent data.
#

## TODO: messaging data link for S2D or D2D
class Message:
    def __init__(self, sock, addr, selector, request):
        self._jsonheader_len = None
        self.jsonheader = None
        self.response = None
        self.sock = sock
        self.addr = addr

        ## Keep track of to and from addresses
        # self.to_addr = None
        # self.from_addr = None

        ## buffer for storing data tempararily
        self._recv_buffer = b""     # Initially an empty byte string
        self._send_buffer = b""
        ## status variables that keep record of queue states

    def _read(self):
        """ Reads data from the socket object.
        """
        try:
            # reads data from sock
            data = self.sock.recv(4096)
        except BlockingIOError:
            # catches any errors and forwards it to __main__
            pass
        else:
            # check if any data was sent; i.e data is not None
            if data:
                self._recv_buffer += data   # add data to buffer
            else:
                raise RuntimeError("Peer closed")


    def _write(self):
        # check if there is something to send
        if self._send_buffer:
            print(f"Sending {repr(self._send_buffer)}  to {self.addr}")
            try:
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                pass
            else:
                # add data onto the send buffer
                self._send_buffer += self._send_buffer[sent:]

    def _json_encode(self, obj, encoding):
        """ Messages need to be encoded and packed as json
        """
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes, encoding, newline="")
        )
        obj = json.load(tiow)
        tiow.close()
        return obj


    def _create_message(self, *, content_bytes, content_type, content_encoding, from_addr):
        # create the json header for the message
        jsonheader = {
            "bytesorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-len": len(content_bytes),
            "address": from_addr,
        }
        # encode the header into bytes
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        # create the final message
        message = message_hdr + jsonheader_bytes + content_bytes

        return message

    def read(self):
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonresponse()

        if self.jsonheader:
            if self.response is None:
                self.process_response()

    def write(self):
        if not self._request_queued:
            self.queued_request()

        self._write()
        if self._request_queued:
            if not self._send_buffer:
                self._set_selectors_event_mask("r")


    def queued_request(self):
        content = self.request["content"]
        content_type = self.request["content-type"]
        content_encoding = self.request["encoding"]

        if content_type == "text/json":
            req = {
                "content_bytes": self._json_encode(content, content_encoding),
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        else:
            req = {
                "content_bytes": content,
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        message = self._create_message(**req)
        self._send_buffer += message
        self._request_queued = True
