import { RenderingModule } from "./src/rendering/renderer";
import * as fs from "fs";

async function test() {
    console.log("Checking RenderingModule compilation...");
    const renderer = new RenderingModule();
    console.log("Renderer instantiated.");
}

test().catch(console.error);
