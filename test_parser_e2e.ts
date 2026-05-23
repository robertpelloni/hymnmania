import { MidiParser } from "./src/analysis/midi_parser";
const dna = MidiParser.parse("hymn_remaker/output/test_vocal/e2e_test.mid");
console.log("DNA extracted:", dna.melody.length > 0);
if (dna.melody.length > 0) console.log("Melody Note:", dna.melody[0].note);
