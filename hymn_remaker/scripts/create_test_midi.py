import struct

def create_simple_midi(filename):
    # SMF Header: MThd, len=6, format=0, tracks=1, division=96
    header = b'MThd\x00\x00\x00\x06\x00\x00\x00\x01\x00\x60'

    # Track Data
    # Delta-time, Event
    # 00 90 3C 40 (Note On, Middle C, Velocity 64)
    # 60 80 3C 40 (Note Off after 96 ticks)
    # 00 FF 2F 00 (End of Track)
    track_events = (
        b'\x00\x90\x3C\x40'  # Note On C4
        b'\x60\x80\x3C\x40'  # Note Off C4
        b'\x00\xFF\x2F\x00'  # End of Track
    )

    # Track Header: MTrk, length
    track_len = struct.pack('>I', len(track_events))
    track_chunk = b'MTrk' + track_len + track_events

    with open(filename, 'wb') as f:
        f.write(header + track_chunk)

    print(f"Created {filename}")

if __name__ == "__main__":
    create_simple_midi("hymn_remaker/input/test_hymn.mid")
