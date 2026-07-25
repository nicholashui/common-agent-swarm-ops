import { mkdir } from "node:fs/promises";
import { resolve } from "node:path";

import { verifyScreenInventory } from "../src/lib/screens/screen-inventory";
import {
  defaultProjectRoot,
  verifyVisualBaselines,
} from "../src/lib/screens/visual-verification";

interface CliOptions {
  readonly outputDirectory: string;
}

function parseOptions(args: readonly string[], rootDirectory: string): CliOptions {
  const outputArgumentIndex = args.indexOf("--output");
  const outputArgument = outputArgumentIndex >= 0 ? args[outputArgumentIndex + 1] : undefined;
  if (outputArgumentIndex >= 0 && (outputArgument === undefined || outputArgument.startsWith("--"))) {
    throw new Error("--output requires a directory path.");
  }
  return { outputDirectory: resolve(rootDirectory, outputArgument ?? "frontend/.artifacts/visual") };
}

async function main(): Promise<void> {
  const rootDirectory = defaultProjectRoot();
  const options = parseOptions(process.argv.slice(2), rootDirectory);
  await mkdir(options.outputDirectory, { recursive: true });
  const visualResult = await verifyVisualBaselines({
    rootDirectory,
    outputDirectory: options.outputDirectory,
  });
  const inventory = await verifyScreenInventory({
    rootDirectory,
    visualOutputDirectory: options.outputDirectory,
  });
  const result = { ...visualResult, inventory };
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  if (!visualResult.passed || !inventory.passed) process.exitCode = 1;
}

main().catch((error: unknown) => {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
  process.exitCode = 1;
});
