import json
from math import ceil
from threading import Lock

import sys

ENCODING = "ascii"

print_lock = Lock()
def s_print(*args, **kwargs):
    """
    Thread-safe print

    https://stackoverflow.com/questions/40356200/python-printing-in-multiple-threads
    """
    with print_lock:
        print(*args, **kwargs)
        sys.stdout.flush()


def error_json(msg):
    return bytes(json.dumps({"error": msg}), encoding=ENCODING)


class MessageHandler():
    max_size = 2**10
    min_header_keys = {"size", "type", "description"}
    accepted_types = {'json', 'midi'}

    def __init__(self, comm_id, socket):
        """

        """
        self.comm_id = comm_id
        self.socket = socket

    def recv(self):
        """
        Blocks and receives data. Handles headers by itself.

        Should be running on a loop on its own thread to allow for
        async listening and querying
        """

        # Receive header and ensure validity
        header = self.socket.recv(self.max_size)
        print(f"Received header '{header}'")
        try:
            header = json.loads(header.decode(ENCODING))
        except json.JSONDecodeError:
            raise Exception("Invalid header. Must be a JSON")

        msg_size = header['size']
        msg_type = header['type']

        # Get message in chunks if necessary
        msg = bytearray()
        chunks = ceil(msg_size / self.max_size)
        for i in range(chunks):
            chunk = self.socket.recv(self.max_size)
            msg.extend(chunk)

        # Decode message
        if msg_type == 'json':
            msg = json.loads(msg.decode(ENCODING))
        elif msg_type == 'bytes':
            pass
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
        print(header)
        header = json.dumps(header).encode(ENCODING)
        if len(header) > self.max_size:
            raise Exception("Header too large")

        # SEND header
        self.socket.send(header)

        # SEND message in multiple chunks if necessary
        msg_ptr = memoryview(msg).cast('B')
        chunks = ceil(len(msg_ptr) / self.max_size)
        for i in range(chunks):
            chunk = msg_ptr[:self.max_size]
            msg_ptr = msg_ptr[self.max_size:]
            self.socket.send(chunk)

    def query(self, action, data):
        """
        Standarized request from client. Doesn't return anything as recvs
        must be handled in a unified place in the client code
        """
        query_msg = json.dumps({"action": action, "data": data})\
                        .encode(ENCODING)
        self.send_message(query_msg)
