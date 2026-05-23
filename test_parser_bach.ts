import { MidiParser } from "./src/analysis/midi_parser";
const dna = MidiParser.parse("hymn_remaker/input/bach-badinerie-piano-solo.mid");
console.log("Melody length:", dna.melody.length);
console.log("Harmony length:", dna.harmony.length);
