import json
from math import ceil


ENCODING = "ascii"


def error_json(msg):
    return bytes(json.dumps({"error": msg}), encoding=ENCODING)


class MessageHandler():
    max_size = 2**10
    min_header_keys = {"size"}

    def __init__(self, socket):
        """

        """
        self.socket = socket

    def get_msg(self):
        failed = False
        msg = self.socket.recv(self.max_size)
        try:
            msg = json.loads(msg)
            if type(msg) != dict or len(msg) == 0:
                failed = True
        except json.JSONDecodeError:
            failed = True

        if failed:
            self.socket.send(error_json("Invalid Message"))
            return None

        return msg

    def get_header(self):
        # Get header
        msg = self.get_msg()
        if not msg:
            return None
        if list(msg.keys())[0] != "header":
            self.socket.send(error_json("First message not a header"))
            return None
        header = msg['header']
        if any((key not in self.min_header_keys for key in header.keys())):
            self.socket.send(error_json("Invalid header"))
            return None

        return header

    def make_query(self, action, data):
        return json.dumps({"action": action, "data": data})\
                   .encode(ENCODING)

    def make_header(self, size):
        hdr = {"header": {"size": size}}
        return json.dumps(hdr).encode(ENCODING)

    def get_chunked_message(self, msg_size):
        chunks = ceil(msg_size / self.max_size)
        msg = bytearray()
        for i in range(chunks):
            msg.extend(self.socket.recv(self.max_size))
        return msg

    def send_message(self, msg, raw_bytes=False):
        # Ensure message is bytes
        if type(msg) != bytes:
            if not raw_bytes:
                msg = json.dumps(msg).encode(ENCODING)
            else:
                raise Exception("Must send bytes if raw_bytes=True")

        # Send header
        self.socket.send(self.make_header(len(msg)))

        # Found out about memoryview from the Python Cookbook. It lets
        # us send long streams of data without copying it
        # unnecessarily!
        mem_view = memoryview(msg).cast('B')
        chunks = ceil(len(mem_view) / self.max_size)
        for i in range(chunks):
            mem = mem_view[:self.max_size]
            mem_view = mem_view[self.max_size:]
            self.socket.send(mem)

    def recv(self, raw_bytes=False):
        # Recv response
        header = self.get_header()
        if not header:
            return None
        msg = self.get_chunked_message(header['size'])
        if not raw_bytes:
            msg = json.loads(msg)
        return msg

    def query(self, query, raw_bytes=False):
        # Send message
        self.send_message(query)
        msg = self.recv(raw_bytes)
        return msg
