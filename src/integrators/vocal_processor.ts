import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import axios from 'axios';

export interface VocalProcessorConfig {
    mode: 'local' | 'api';
    lalalApiKey?: string;
    targetBpm: number;
    targetKey?: string;
}

export class VocalProcessor {
    private config: VocalProcessorConfig;

    constructor(config: VocalProcessorConfig) {
        this.config = config;
    }

    async process(inputPath: string, outputDir: string): Promise<string> {
        console.log(`Starting vocal processing for ${inputPath}...`);

        // 1. Demixing
        const vocalStem = await this.isolateVocals(inputPath, outputDir);

        // 2. Analysis (BPM/Key)
        const analysis = await this.analyzeAudio(vocalStem);
        console.log(`Analysis: BPM=${analysis.bpm}, Key=${analysis.key}`);

        // 3. Time Stretch
        const stretchedPath = this.timeStretch(vocalStem, analysis.bpm, this.config.targetBpm);

        // 4. Pitch Shift (Placeholder for key alignment)
        // In a real scenario, we'd calculate semitone diff between analysis.key and config.targetKey
        const finalPath = stretchedPath; // Assume alignment for now or implement rubberband call

        return finalPath;
    }

    private async isolateVocals(inputPath: string, outputDir: string): Promise<string> {
        if (this.config.mode === 'local') {
            console.log("Running Demucs locally...");
            const cmd = `python3 -m demucs.separate --two-stems=vocals -o ${outputDir} "${inputPath}"`;
            execSync(cmd);

            const nameNoExt = path.basename(inputPath, path.extname(inputPath));
            // Demucs output structure: outputDir/htdemucs/filename/vocals.wav
            return path.join(outputDir, 'htdemucs', nameNoExt, 'vocals.wav');
        } else {
            console.log("LALAL.AI API integration (stub)...");
            // Implement REST call to LALAL.AI here
            throw new Error("LALAL.AI API mode not fully implemented yet.");
        }
    }

    private async analyzeAudio(filePath: string): Promise<{ bpm: number, key: string }> {
        console.log("Analyzing audio via Python helper...");
        // Use a simple python snippet to get BPM using librosa
        const pythonScript = `
import librosa
import sys
y, sr = librosa.load("${filePath}")
tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
# Key detection is more complex, returning a stub
print(f"{float(tempo)},Cmin")
`;
        const result = execSync(`python3 -c '${pythonScript}'`).toString().trim();
        const [bpm, key] = result.split(',');
        return { bpm: parseFloat(bpm), key };
    }

    private timeStretch(inputPath: string, originalBpm: number, targetBpm: number): string {
        const ratio = targetBpm / originalBpm;
        const outputPath = inputPath.replace(".wav", "_stretched.wav");
        console.log(`Time-stretching: ${originalBpm} -> ${targetBpm} (Ratio: ${ratio.toFixed(3)})`);

        // FFmpeg atempo filter (chained if ratio > 2.0 or < 0.5)
        let filter = `atempo=${ratio}`;
        if (ratio > 2.0) filter = `atempo=2.0,atempo=${ratio/2.0}`;
        if (ratio < 0.5) filter = `atempo=0.5,atempo=${ratio/0.5}`;

        const cmd = `ffmpeg -y -i "${inputPath}" -filter:a "${filter}" "${outputPath}"`;
        execSync(cmd);
        return outputPath;
    }
}
