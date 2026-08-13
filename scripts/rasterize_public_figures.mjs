/** Rasterize editable SVG presentation figures to high-resolution PNG. */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dir = path.join(root, "figures", "public_evidence");
for (const name of fs.readdirSync(dir).filter((x) => x.endsWith(".svg"))) {
  const src = path.join(dir, name);
  const dst = path.join(dir, name.replace(/\.svg$/i, ".png"));
  await sharp(src, { density: 180 }).flatten({ background: "#ffffff" }).png().toFile(dst);
  console.log(dst);
}
