import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const FRONTEND_ROOT = resolve(SCRIPT_DIR, "..");
const generator = resolve(SCRIPT_DIR, "generate-api-client.mjs");
const committed = resolve(FRONTEND_ROOT, "src/lib/api/generated/index.ts");
const temporaryDirectory = await mkdtemp(resolve(tmpdir(), "frontend-api-client-"));
const temporaryOutput = resolve(temporaryDirectory, "index.ts");

function runGenerator() {
  return new Promise((resolvePromise, rejectPromise) => {
    const child = spawn(process.execPath, [generator, "--output", temporaryOutput], { cwd: FRONTEND_ROOT, stdio: "inherit" });
    child.once("error", rejectPromise);
    child.once("exit", (code) => code === 0 ? resolvePromise() : rejectPromise(new Error(`Generated-client command failed with exit code ${code}.`)));
  });
}

try {
  await runGenerator();
  const [expected, actual] = await Promise.all([readFile(temporaryOutput), readFile(committed)]);
  if (!expected.equals(actual)) throw new Error("Generated client drift detected. Run npm run api:generate and commit the result.");
} finally {
  await rm(temporaryDirectory, { force: true, recursive: true });
}
