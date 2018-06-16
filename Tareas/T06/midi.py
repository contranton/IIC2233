from functools import reduce


class MIDIReaderFormatNotImplemented(Exception):
    pass


class MIDIReaderInvalidTrack(Exception):
    pass


class MIDIReaderInvalidFile(Exception):
    pass


class MIDIFile():
    def __init__(self, midi_format, n_tracks, time_div):
        """

        """
        self.chunk_Type = 'MThd'.encode('ascii')
        self.midi_format = midi_format
        self.n_tracks = n_tracks
        self.time_div = time_div

    @property
    def length(self):
        pass


class MIDITrack():
    pass


class MIDINote():
    pass


_event_names = {8: "NoteOFF",
                9: "NoteON"}


def get_int(bytes_):
    return int.from_bytes(bytes_, byteorder='big')


def load_midi(file_path):
    with open(file_path, 'rb') as file:
        header = file.read(4)
        if header.decode("ascii") != "MThd":
            raise MIDIReaderInvalidFile()
        length = get_int(file.read(4))  # Header length is always 6
        formt = get_int(file.read(2))   # MIDI format
        ntrks = get_int(file.read(2))   # Number of tracks
        divsn = get_int(file.read(2))   # Time division in ticks per 1/4 note

        print(f"{header.decode('ascii')} -- Len={length} -- Frmt={formt} -- "
              f"Tracks={ntrks} -- TimeDiv={divsn}")

        while True:
            # Read tracks until EOF

            hdr = file.read(4)
            if not hdr:
                break

            if hdr.decode("ascii") != "MTrk":
                raise MIDIReaderInvalidTrack()

            tr_length = get_int(file.read(4))

            # Delta is variable length. According to the convention, only
            # the last byte for this value will have the MSB zero. In case
            # the value is less than 127, i.e. MSB=0, the delta is
            # effectively the single byte

            # Decode the MIDI events
            while True:

                # We have to do bit manipulation, which bytearray isn't good at
                time = []

                time_got = False
                while not time_got:
                    delta = get_int(file.read(1))
                    # If MSB is 0 we've reached the last time byte
                    if delta & 128 == 0:  # X & 128 applies the mask 1000 0000
                        time_got = True
                    # X & 127 applies the mask 0111 1111
                    time.append(delta & 127)

                # Concatenates the 7-bit values together
                time = reduce(lambda x, y: x << 7 | y, time)

                type_and_channel = get_int(file.read(1))

                if type_and_channel == 0xFF:  # FF denotes a MIDI meta event
                    meta_code = get_int(file.read(1))

                    # Our implementation only accepts the meta event
                    # TRACK END
                    if meta_code == 0x2F:
                        # Next byte should be 0 for TRACK END
                        assert get_int(file.read(1)) == 0
                        break
                    else:
                        raise MIDIReaderFormatNotImplemented()
                    continue

                event_type = (type_and_channel & 0xF0) >> 4
                channel = type_and_channel & 0x0F
                note = get_int(file.read(1))
                velocity = get_int(file.read(1))

                print(f"{_event_names[event_type]} -- Time={time} -- "
                      f"Pitch={note} -- Vel={velocity} -- Channel={channel}")
