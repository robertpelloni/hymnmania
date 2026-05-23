import os
import subprocess
from hymn_remaker.src.audio_to_midi import transcribe_audio_to_midi

audio_in = 'hymn_remaker/output/test_vocal/sine_440.wav'
midi_out = 'hymn_remaker/output/test_vocal/e2e_test.mid'

# 1. Transcribe
transcribe_audio_to_midi(audio_in, midi_out)

# 2. Extract DNA via TS
cmd = ['npx', 'ts-node', '--transpile-only', 'test_parser.ts']
# Update test_parser.ts to use e2e_test.mid
with open('test_parser_e2e.ts', 'w') as f:
    f.write('import { MidiParser } from "./src/analysis/midi_parser";\n')
    f.write(f'const dna = MidiParser.parse("{midi_out}");\n')
    f.write('console.log("DNA extracted:", dna.melody.length > 0);\n')
    f.write('if (dna.melody.length > 0) console.log("Melody Note:", dna.melody[0].note);\n')

result = subprocess.run(['npx', 'ts-node', '--transpile-only', 'test_parser_e2e.ts'], capture_output=True, text=True)
print(result.stdout)
