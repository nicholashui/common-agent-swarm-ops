export function report(title, entries) {
  console.log(title); for (const [key, value] of Object.entries(entries)) console.log(`${key}: ${value}`);
}
export function fail(message) { console.error(`ERROR: ${message}`); process.exitCode = 1; }
