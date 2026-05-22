import { Midi } from "@tonejs/midi";
import { HymnDNA } from "../analysis/midi_parser";
import * as fs from "fs";

export class PsyGenerator {
    static generate(dna: HymnDNA, targetBpm: number = 145): Midi {
        const midi = new Midi();
        midi.header.setTempo(targetBpm);
        midi.header.name = dna.title + " (Psytrance Remix)";

        const kickTrack = midi.addTrack();
        kickTrack.name = "Kick";

        const bassTrack = midi.addTrack();
        bassTrack.name = "Bass";

        const leadTrack = midi.addTrack();
        leadTrack.name = "Lead Arp";

        const duration = dna.melody.length > 0 ? dna.melody[dna.melody.length - 1].time + 2 : 60;
        for (let t = 0; t < duration; t += 60 / targetBpm) {
            kickTrack.addNote({
                midi: 36,
                time: t,
                duration: 0.1,
                velocity: 0.9
            });
        }

        const sixteenth = 60 / targetBpm / 4;
        for (let i = 0; i < duration / sixteenth; i++) {
            const time = i * sixteenth;
            const barIndex = Math.floor(i / 16);
            const slotInBeat = i % 4;

            if (slotInBeat !== 0) { // Off-beats (slots 2, 3, 4 of the beat)
                // Find harmony note at this time
                const activeHarmony = dna.harmony.find(h => h.time <= dna.melody[0]?.time + time * (dna.bpm / targetBpm)) || dna.harmony[0];
                let rootNote = activeHarmony ? (activeHarmony.note % 12) + 36 : 36; // Keep it in bass range

                // Octave-jump toggle on the 4th slot (index 3) of alternating bars
                if (slotInBeat === 3 && barIndex % 2 === 1) {
                    rootNote += 12;
                }

                bassTrack.addNote({
                    midi: rootNote,
                    time: time,
                    duration: sixteenth * 0.8,
                    velocity: 0.7
                });
            }
        }

        const euclideanPattern = [1, 0, 1, 1, 0, 1, 1, 0];
        for (let i = 0; i < duration / sixteenth; i++) {
            const time = i * sixteenth;
            if (euclideanPattern[i % euclideanPattern.length] === 1) {
                const scaledTime = time * (dna.bpm / targetBpm);
                const activeMelody = dna.melody.find(m => m.time <= scaledTime && m.time + m.duration >= scaledTime) || dna.melody.find(m => m.time > scaledTime);

                if (activeMelody) {
                    leadTrack.addNote({
                        midi: activeMelody.note,
                        time: time,
                        duration: sixteenth * 0.5,
                        velocity: 0.8
                    });
                }
            }
        }

        return midi;
    }

    static saveMidi(midi: Midi, outputPath: string) {
        fs.writeFileSync(outputPath, Buffer.from(midi.toArray()));
    }
}
