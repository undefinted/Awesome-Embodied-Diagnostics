/** Rasterize one SVG to PNG with explicit input/output paths.
 * Usage: node rasterize_svg.mjs input.svg output.png [density]
 */
import { createRequire } from "node:module";
import path from "node:path";

// createRequire honours NODE_PATH, allowing the reproducibility script to use
// either a local sharp installation or the bundled Codex workspace runtime.
const require = createRequire(import.meta.url);
const sharp = require("sharp");

const [, , input, output, densityArg] = process.argv;
if (!input || !output) {
  console.error("Usage: node rasterize_svg.mjs input.svg output.png [density]");
  process.exit(2);
}
const density = Number(densityArg || 180);
await sharp(path.resolve(input), { density })
  .flatten({ background: "#ffffff" })
  .png()
  .toFile(path.resolve(output));
console.log(path.resolve(output));
