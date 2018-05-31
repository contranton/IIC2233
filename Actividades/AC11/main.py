import os
import os.path as path

from string import ascii_lowercase, ascii_uppercase

numbers = "".join([str(i) for i in range(10)])


def fib():
    a, b = 0, 1
    c = 1
    while True:
        yield c
        c = a + b
        a = b
        b = c


def next_4_sizes():
    i = 0
    f = fib()
    while True:
        yield next(f), next(f), next(f), next(f)


# Danke schon
# https://stackoverflow.com/questions/1124810/how-can-i-find-path-to-given-file
path_names = ["marciano64", "marcianozurdo"]
paths = {}

for root, dirs, files in os.walk('.'):
    for name in files:
        nm = name.split(".")[0]
        if nm in path_names:
            paths[nm] = path.abspath(path.join(root, name))

_b64_trans = str.maketrans(
    ascii_uppercase + ascii_lowercase + numbers + "+/",
    "".join([chr(i) for i in range(64)]))


def base64(my_bytes):
    # Assuming ascii encoding
    new_bytes = []
    for byte in my_bytes:
        new_byte = _b64_trans[byte]
        new_byte = bin(new_byte)[2:].zfill(6)
        [new_bytes.append(nb) for nb in new_byte]
    new_bytes = "".join(new_bytes)
    new_ints = [new_bytes[i:i+8] for i in range(len(new_bytes)//8)]

    new_ints = [int("0b" + i, 2) for i in new_ints]

    return new_ints


def rotleft(hunk):
    return bytearray([hunk[(i-1)%len(hunk)] for i in range(len(hunk))])


def merge_files():

    with open(paths["marciano64"], 'rb') as file64:
        with open("newmarciano64.png", 'wb') as newfile:
            newfile.write(bytearray(base64(file64.read())))

    final_bytearray = bytearray()
    with open(paths["marcianozurdo"], 'rb') as filepep, open("newmarciano64.png", 'rb') as file64:
        for size1, size2, size3, size4 in next_4_sizes():
            chunks = [rotleft(filepep.read(size1)),
                      file64.read(size2),
                      rotleft(filepep.read(size3)),
                      file64.read(size4)]
            [final_bytearray.extend(chunk) for chunk in chunks]
    with open("resultado.png", 'bw') as f:
        f.write(final_bytearray)


if __name__ == '__main__':
    # merge_files()
    pass
