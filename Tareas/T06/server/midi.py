import os
from functools import reduce
from collections import deque


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
        self.chunk_type = 'MThd'.encode('ascii')
        if midi_format == 1:
            self.midi_format = midi_format
        else:
            raise MIDIReaderFormatNotImplemented(
                "Only MIDI Format 1 supported")
        self.n_tracks = n_tracks
        self.time_div = time_div

        self.tracks = []

    def __repr__(self):
        return f"MidiFile({len(self.tracks)} tracks)"

    def to_bytes(self):
        b_type = self.chunk_type
        b_length = self.length
        b_format = int.to_bytes(self.midi_format, 2, 'big')
        b_ntrks = int.to_bytes(self.n_tracks, 2, 'big')
        b_time_div = int.to_bytes(self.time_div, 2, 'big')

        b_tracks = reduce(lambda i, j: i + j.as_bytes, self.tracks, b'')

        return b_type + b_length + b_format + b_ntrks + b_time_div + b_tracks

    @property
    def length(self):
        return b'\x00\x00\x00\x06'

    def add_track(self, track):
        self.tracks.append(track)


class MIDITrack():
    def __init__(self):
        """

        """
        self.hdr = "MTrk".encode('ascii')
        self.events = deque()

        self.as_bytes = self.to_bytes()

    def __repr__(self):
        return f"Track({len(self.events)} notes)"

    def add_event(self, event):
        self.events.append(event)
        self.as_bytes = self.to_bytes()

    def to_bytes(self):
        b_hdr = self.hdr
        b_events = reduce(lambda i, j: i + j.as_bytes, self.events, b'')
        b_end_event = b'\x00\xFF\x2F\x00'

        b_length = int.to_bytes(len(b_events + b_end_event), 4, 'big')

        return b_hdr + b_length + b_events + b_end_event

    @property
    def length(self):
        # Must add meta event length
        return len(self.as_bytes)


class MIDINoteEvent():
    def __init__(self, time_delta, event_type, channel, pitch, velocity):
        """

        """
        self.time_delta = time_delta
        if event_type not in _event_names.keys():
            raise MIDIReaderFormatNotImplemented(
                "Only NoteON and NoteOFF MIDI events supported")
        else:
            self.event_type = event_type
        self.channel = channel
        self.pitch = pitch
        self.velocity = velocity

        self.as_bytes = self._to_bytes()

    def __repr__(self):
        return (f"{_event_names[self.event_type]}(Time={self.time_delta},"
                f"Pitch={self.pitch}, Vel={self.velocity})")

    @property
    def length(self):
        return len(self.as_bytes)

    def _to_bytes(self):
        b_time_delta = self.get_time_bytes()
        b_event_byte = int.to_bytes(self.event_type << 4 + self.channel, 1,
                                    byteorder='big')
        b_pitch = int.to_bytes(self.pitch, 1, byteorder='big')
        b_velocity = int.to_bytes(self.velocity, 1, byteorder='big')

        return b_time_delta + b_event_byte + b_pitch + b_velocity

    def get_time_bytes(self):
        delta = self.time_delta
        if delta == 0:
            return b'\x00'

        # Break down time into 7 bit words
        delta_bytes = []
        while delta > 0:
            delta_bytes.append(delta & 0x7F)  # 0x7F = 0111 1111
            delta >>= 7

        # Adds MSB 1 or 0 as corresponds
        delta_bytes = [j | (0x80*(i != 0))
                       for (i, j) in enumerate(delta_bytes)]

        return reduce(lambda i, j: i + int.to_bytes(j, 1, byteorder='big'),
                      delta_bytes[::-1], b'')


_event_names = {8: "NoteOFF",
                9: "NoteON"}


def get_int(bytes_):
    return int.from_bytes(bytes_, byteorder='big')


def load_midi(file_path):
    # TODO: Modularize
    with open(file_path, 'rb') as file:
        header = file.read(4)
        if header.decode("ascii") != "MThd":
            raise MIDIReaderInvalidFile()
        length = get_int(file.read(4))  # Header length is always 6
        formt = get_int(file.read(2))   # MIDI format
        ntrks = get_int(file.read(2))   # Number of tracks
        divsn = get_int(file.read(2))   # Time division in ticks per 1/4 note

        midi_file = MIDIFile(formt, ntrks, divsn)

        while True:
            # Read tracks until EOF

            hdr = file.read(4)
            if not hdr:
                break

            if hdr.decode("ascii") != "MTrk":
                raise MIDIReaderInvalidTrack()

            tr_length = get_int(file.read(4))

            midi_track = MIDITrack()
            midi_file.add_track(midi_track)

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
                        raise MIDIReaderFormatNotImplemented(
                            "Only meta code FF 2F suuported")
                    continue

                event_type = (type_and_channel & 0xF0) >> 4
                channel = type_and_channel & 0x0F  # Should always be 0
                if channel != 0:
                    raise MIDIReaderFormatNotImplemented(
                        "Only channel 0 is supported")
                pitch = get_int(file.read(1))
                velocity = get_int(file.read(1))

                note = MIDINoteEvent(time, event_type, channel, pitch,
                                     velocity)

                midi_track.add_event(note)

    return midi_file


def test_read_write_midi():
    for midi, name, path in get_midis():
        with open(path, 'rb') as f:
            midi_original = f.read()
        if midi.to_bytes() == midi_original:
            print(f"{file:25} passed")
        else:
            print(f"{file:25} passed")


def get_midis():
    for root, dirs, files in os.walk("midis"):
        for name in files:
            path = root + "\\" + name
            midi = load_midi(path)
            print(f"Loaded {name}")
            yield midi, name, path


if __name__ == '__main__':
    test_read_write_midi()