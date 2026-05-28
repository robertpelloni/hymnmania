import mido
import math
import random
from mido import Message, MidiFile, MidiTrack, MetaMessage

class PsyGenerator:
    def __init__(self):
        self.ticks_per_beat = 480
        self.ticks_per_sixteenth = self.ticks_per_beat // 4

    def generate(self, input_midi_path, output_midi_path, config):
        """
        Generates a 145 BPM Psytrance pattern based on input MIDI.
        """
        try:
            input_mid = MidiFile(input_midi_path)
        except Exception:
            # Fallback if no input file
            input_mid = None

        output_mid = MidiFile(ticks_per_beat=self.ticks_per_beat)

        bpm = config.get("targetBpm", 145)
        tempo = mido.bpm2tempo(bpm)

        # Extract melody and chords from input
        melody_notes, root_notes = self._extract_dna(input_mid)

        # 1. Kick Track
        output_mid.tracks.append(self._generate_kick(tempo, config))

        # 2. Bass Track
        output_mid.tracks.append(self._generate_bass(root_notes, config))

        # 3. Lead Track
        output_mid.tracks.append(self._generate_lead(melody_notes, config))

        output_mid.save(output_midi_path)
        return True

    def _extract_dna(self, mid):
        melody = [] # list of (start_tick, note, duration_tick)
        roots = []  # list of (start_tick, note)

        if not mid:
            return melody, roots

        # Simplistic extraction: Highest notes for melody, lowest for roots
        all_notes = []
        for track in mid.tracks:
            abs_tick = 0
            active_notes = {}
            for msg in track:
                abs_tick += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    active_notes[msg.note] = abs_tick
                elif (msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)) and msg.note in active_notes:
                    start = active_notes.pop(msg.note)
                    all_notes.append({'note': msg.note, 'start': start, 'end': abs_tick})

        if not all_notes:
            return melody, roots

        all_notes.sort(key=lambda x: x['start'])

        # Segment by 4-bar blocks (assuming 4/4)
        total_ticks = max(n['end'] for n in all_notes)
        ticks_per_bar = self.ticks_per_beat * 4

        for bar_start in range(0, total_ticks, ticks_per_bar):
            bar_notes = [n for n in all_notes if bar_start <= n['start'] < bar_start + ticks_per_bar]
            if bar_notes:
                highest = max(bar_notes, key=lambda x: x['note'])
                lowest = min(bar_notes, key=lambda x: x['note'])
                melody.append((bar_start, highest['note'], ticks_per_bar))
                roots.append((bar_start, lowest['note']))

        return melody, roots

    def _generate_kick(self, tempo, config):
        track = MidiTrack()
        track.append(MetaMessage('set_tempo', tempo=tempo))
        track.append(MetaMessage('track_name', name='Kick'))

        vel = int(config.get("kickVelocity", 0.9) * 127)
        for _ in range(8): # 8 bars
            for _ in range(4): # 4 beats
                track.append(Message('note_on', note=36, velocity=vel, time=0))
                track.append(Message('note_off', note=36, velocity=0, time=self.ticks_per_sixteenth))
                track.append(Message('note_on', note=0, velocity=0, time=0)) # Dummy padding
                track.append(Message('note_off', note=0, velocity=0, time=self.ticks_per_sixteenth * 3))
        return track

    def _generate_bass(self, root_notes, config):
        track = MidiTrack()
        track.append(MetaMessage('track_name', name='Bass'))

        vel = int(config.get("bassVelocity", 0.7) * 127)
        variant = config.get("gallopVariant", "classic")
        octave_freq = config.get("octaveJumpBarFrequency", 2)

        curr_root = 36 # Default C1
        root_idx = 0

        for bar in range(8):
            if root_idx < len(root_notes):
                curr_root = (root_notes[root_idx][1] % 12) + 36
                root_idx += 1

            for beat in range(4):
                # Psytrance bass is on the offbeats (16th slots 2, 3, 4)
                # Slot 1: Silence (Kick)
                track.append(Message('note_on', note=0, velocity=0, time=0))
                track.append(Message('note_off', note=0, velocity=0, time=self.ticks_per_sixteenth))

                for slot in range(2, 5):
                    note = curr_root
                    # Octave jump on slot 4 occasionally
                    if slot == 4 and octave_freq > 0 and bar % octave_freq == 0:
                        note += 12

                    if variant == "triplet" and slot == 2:
                        # Skip first bass note for triplet feel
                        track.append(Message('note_on', note=0, velocity=0, time=0))
                        track.append(Message('note_off', note=0, velocity=0, time=self.ticks_per_sixteenth))
                    else:
                        track.append(Message('note_on', note=note, velocity=vel, time=0))
                        track.append(Message('note_off', note=note, velocity=0, time=self.ticks_per_sixteenth))
        return track

    def _generate_lead(self, melody_notes, config):
        track = MidiTrack()
        track.append(MetaMessage('track_name', name='Lead'))

        vel = int(config.get("leadVelocity", 0.8) * 127)
        density = config.get("euclideanDensity", 5)
        use_markov = config.get("useMarkovLeads", True)

        # Simple Euclidean pattern E(density, 16)
        pattern = [0] * 16
        if density > 0:
            for i in range(density):
                pattern[(i * 16 // density) % 16] = 1

        curr_melody_note = 60 # C3
        melody_idx = 0

        # Markov Chain state
        last_note = curr_melody_note

        for bar in range(8):
            if melody_idx < len(melody_notes):
                curr_melody_note = (melody_notes[melody_idx][1] % 24) + 60
                melody_idx += 1

            # Simple Psytrance Markov Transition Rules:
            # - 70% chance to stay on current note or move by small interval
            # - 20% chance to jump by +3, +7, or +12 (perfect intervals/octave)
            # - 10% chance to jump back to hymn's current anchor note

            for slot in range(16):
                if pattern[slot]:
                    note = last_note
                    if use_markov:
                        r = random.random()
                        if r < 0.7:
                            note = last_note + random.choice([-1, 0, 1, 2])
                        elif r < 0.9:
                            note = last_note + random.choice([3, 7, 12, -12])
                        else:
                            note = curr_melody_note

                        # Clamp to reasonable range (C3 to C5)
                        note = max(48, min(84, note))
                    else:
                        note = curr_melody_note

                    track.append(Message('note_on', note=note, velocity=vel, time=0))
                    track.append(Message('note_off', note=note, velocity=0, time=self.ticks_per_sixteenth))
                    last_note = note
                else:
                    track.append(Message('note_on', note=0, velocity=0, time=0))
                    track.append(Message('note_off', note=0, velocity=0, time=self.ticks_per_sixteenth))
        return track
