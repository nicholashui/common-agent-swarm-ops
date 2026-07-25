import { resolve } from "node:path";

import { verifyScreenInventory } from "../src/lib/screens/screen-inventory";
import { defaultProjectRoot } from "../src/lib/screens/visual-verification";

function parseOutputDirectory(args: readonly string[], rootDirectory: string): string {
  const outputArgumentIndex = args.indexOf("--output");
  const outputArgument =
    outputArgumentIndex >= 0 ? args[outputArgumentIndex + 1] : undefined;
  if (
    outputArgumentIndex >= 0 &&
    (outputArgument === undefined || outputArgument.startsWith("--"))
  ) {
    throw new Error("--output requires a directory path.");
  }
  return resolve(
    rootDirectory,
    outputArgument ?? "frontend/.artifacts/visual",
  );
}

async function main(): Promise<void> {
  const rootDirectory = defaultProjectRoot();
  const visualOutputDirectory = parseOutputDirectory(
    process.argv.slice(2),
    rootDirectory,
  );
  const result = await verifyScreenInventory({
    rootDirectory,
    visualOutputDirectory,
  });
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  if (!result.passed) process.exitCode = 1;
}

main().catch((error: unknown) => {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
  process.exitCode = 1;
});
