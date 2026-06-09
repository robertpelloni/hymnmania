import mido

def inspect(path):
    print(f"Inspecting {path}")
    mid = mido.MidiFile(path)
    for i, track in enumerate(mid.tracks):
        print(f"Track {i}: {track.name} - {len(track)} messages")
        # Check first few notes
        notes = [m for m in track if m.type == 'note_on']
        if notes:
            print(f"  First 5 notes: {notes[:5]}")

inspect("pipeline/output/house_skeletons/Emmanuel_house.mid")
