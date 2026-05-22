import mido

def analyze(path):
    print(f"--- Analyzing {path} ---")
    mid = mido.MidiFile(path)
    for i, track in enumerate(mid.tracks):
        print(f"Track {i}: {track.name}")
        notes = [msg for msg in track if msg.type == 'note_on']
        print(f"  Note count: {len(notes)}")
        if notes:
            avg_vel = sum(n.velocity for n in notes) / len(notes)
            print(f"  Avg velocity: {avg_vel:.2f}")

analyze("hymn_remaker/output/verify_psy_default.mid")
analyze("hymn_remaker/output/verify_psy_custom.mid")
