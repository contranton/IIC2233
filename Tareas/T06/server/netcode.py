import json
import time

from math import ceil, log2
from threading import Lock

import sys

ENCODING = "ascii"

def error_json(msg):
    return bytes(json.dumps({"error": msg}), encoding=ENCODING)


class MessageHandler():
    max_size = 2**10
    min_header_keys = {"size", "type", "description"}
    accepted_types = {'json', 'midi'}

    def __init__(self, id_, socket):
        """

        """
        self.id_ = id_
        self.socket = socket

    @staticmethod
    def t_print(time_, client, action, details):
        print(f"{time_:^20} | {client:^10} | {action:^20} |   {details}")
        
    def log(self, action, details="-"):
        self.t_print(time.strftime('%y/%m/%d - %H:%M:%S', time.localtime()),
                     self.id_,
                     action,
                     details)

    def recv(self):
        """
        Blocks and receives data. Handles headers by itself.

        Should be running on a loop on its own thread to allow for
        async listening and querying
        """

        # RECV header size
        hdr_size = self.socket.recv(ceil(log2(self.max_size)))
        hdr_size = int.from_bytes(hdr_size, 'big')

        # RECV header and ensure validity
        header = self.socket.recv(hdr_size)
        try:
            header = json.loads(header.decode(ENCODING))
        except json.JSONDecodeError:
            raise Exception("Invalid header. Must be a JSON")

        msg_size = header['size']
        msg_type = header['type']

        # RECV message in chunks if necessary
        msg = bytearray()
        chunks = ceil(msg_size / self.max_size)
        for i in range(chunks):
            chunk = self.socket.recv(self.max_size)
            msg.extend(chunk)

        # Decode message
        if msg_type == 'json':
            msg = json.loads(msg.decode(ENCODING))
            vals = (i for i in msg.values())  # There should always be two
            v1 = next(vals)
            v2 = next(vals) if v1 not in {"midi_notes", "midi_list",
                                          "chat_message"} else ""
            self.log(v1, v2)
        elif msg_type == 'midi':
            self.log('midi_download', f"{len(msg)} bytes")
        else:
            raise Exception(f"Server can't handle message type '{msg_type}'")

        return header, msg

    def send_message(self, msg, msg_type='json', descr=''):
        """
        Sends message to connected socket
        """
        # Ensure type consistency
        if msg_type not in self.accepted_types:
            raise Exception(f"Server can't handle message type '{msg_type}'")

        if msg_type == 'json' and type(msg) != bytes:
            msg = json.dumps(msg).encode(ENCODING)

        # Create header
        header = {"size": len(msg),
                  "type": msg_type,
                  "descr": descr}
        header = json.dumps(header).encode(ENCODING)
        if len(header) > self.max_size:
            raise Exception("Header too large")

        self.log(f'send_{msg_type}', descr)
        
        # SEND header size
        self.socket.send(int.to_bytes(len(header), ceil(log2(self.max_size)),
                                      'big'))

        # SEND header
        self.socket.send(header)

        # SEND message in multiple chunks if necessary
        msg_ptr = memoryview(msg).cast('B')
        chunks = ceil(len(msg_ptr) / self.max_size)
        for i in range(chunks):
            chunk = msg_ptr[:self.max_size]
            msg_ptr = msg_ptr[self.max_size:]
            self.socket.send(chunk)

    def query(self, action, *data):
        """
        Standarized request from client. Doesn't return anything as recvs
        must be handled in a unified place in the client code
        """
        query_msg = json.dumps({"action": action, "data": data})\
                        .encode(ENCODING)
        self.send_message(query_msg, descr=action)
