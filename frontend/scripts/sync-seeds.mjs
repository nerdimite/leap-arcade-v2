// Vendors the backend game seeds into the frontend so Storybook stories (and
// tests) can render real tournament content without reaching across the package
// boundary. Run `npm run sync:seeds` whenever the backend seeds change.
//
// Source of truth: backend/leap/seeds/data/*.json (+ backend/leap/seeds/picture.json)
// Destination:     frontend/src/test/seeds/*.json (git-tracked vendored copies)

import { copyFileSync, mkdirSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, "..", "..");
const seedRoot = join(repoRoot, "backend", "leap", "seeds");
const dataDir = join(seedRoot, "data");
const destDir = join(here, "..", "src", "test", "seeds");

mkdirSync(destDir, { recursive: true });

const sources = [
  // picture lives one level up from the rest
  join(seedRoot, "picture.json"),
  ...readdirSync(dataDir)
    .filter((name) => name.endsWith(".json"))
    .map((name) => join(dataDir, name)),
];

let copied = 0;
for (const src of sources) {
  const name = src.split(/[\\/]/).pop();
  copyFileSync(src, join(destDir, name));
  copied += 1;
  console.log(`  vendored ${name}`);
}

console.log(`synced ${copied} seed file(s) -> src/test/seeds/`);
