/** Rasterize one SVG to PNG with explicit input/output paths.
 * Usage: node rasterize_svg.mjs input.svg output.png [density]
 */
import sharp from "sharp";
import path from "node:path";

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

