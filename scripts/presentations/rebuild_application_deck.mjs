import fs from "node:fs/promises";
import path from "node:path";
import { PresentationFile } from "@oai/artifact-tool";

const [sourceArg, outputArg] = process.argv.slice(2);
if (!sourceArg || !outputArg) {
  throw new Error("Usage: node rebuild_application_deck.mjs <source.pptx> <output.pptx>");
}

const source = path.resolve(sourceArg);
const output = path.resolve(outputArg);
await fs.mkdir(path.dirname(output), { recursive: true });

const deck = await PresentationFile.importPptx(await fs.readFile(source));
const exported = await PresentationFile.exportPptx(deck);
await exported.save(output);
console.log(`Exported ${output}`);
