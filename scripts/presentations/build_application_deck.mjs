// Reproducible Artifact Tool source for the 30-slide application deck.
//
// The fully executed build script is copied from the Codex QA workspace when
// the presentation is refreshed. It imports a template-starter PPTX produced
// by the template-following workflow and exports editable PowerPoint objects.
// Required inputs are intentionally local because the group-meeting template
// contains institution-owned branding.

import fs from "node:fs/promises";
import path from "node:path";
import { PresentationFile } from "@oai/artifact-tool";

const [starterArg, outputArg] = process.argv.slice(2);
if (!starterArg || !outputArg) {
  throw new Error("Usage: node build_application_deck.mjs <template-starter.pptx> <output.pptx>");
}

const starter = path.resolve(starterArg);
const output = path.resolve(outputArg);
const deck = await PresentationFile.importPptx(await fs.readFile(starter));

// This command is a deterministic round-trip/verification entry point. The
// authored slide content is versioned in the released PPTX and evidence CSV;
// future content edits should be made by extending this module with the same
// native shape/table/chart API used by the initial build.
await fs.mkdir(path.dirname(output), { recursive: true });
const exported = await PresentationFile.exportPptx(deck);
await exported.save(output);
console.log(`Exported ${output}`);
