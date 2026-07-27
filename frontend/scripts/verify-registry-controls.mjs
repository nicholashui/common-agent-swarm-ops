import puppeteer from "puppeteer-core";

const browser = await puppeteer.launch({
  executablePath:
    process.env.CHROME_PATH ||
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  headless: true,
  args: ["--no-sandbox", "--disable-gpu"],
});

const page = await browser.newPage();
page.on("pageerror", (e) => console.log("PAGEERROR", e.message));
page.on("console", (m) => {
  if (m.type() === "error") console.log("CONERR", m.text());
});

await page.goto("http://127.0.0.1:3001/registry", {
  waitUntil: "networkidle0",
  timeout: 120000,
});
await page.waitForSelector('input[name="registry-search"]', { timeout: 60000 });
await new Promise((r) => setTimeout(r, 2500));

const before = await page.$eval("#registry-agent-results", (el) => el.textContent);
console.log("before", before);

await page.click('input[name="registry-search"]');
await page.type('input[name="registry-search"]', "orchestrator", { delay: 15 });
await new Promise((r) => setTimeout(r, 600));
const afterSearch = await page.$eval(
  "#registry-agent-results",
  (el) => el.textContent,
);
console.log("afterSearch", afterSearch);

await page.evaluate(() => {
  const btns = [...document.querySelectorAll("button")];
  btns.find((b) => b.textContent.trim() === "Table")?.click();
});
await new Promise((r) => setTimeout(r, 400));
const tableView = await page.$eval("[data-registry-view]", (el) =>
  el.getAttribute("data-registry-view"),
);
console.log("view", tableView);

// clear search then specials facet
await page.click('input[name="registry-search"]', { clickCount: 3 });
await page.keyboard.press("Backspace");
await new Promise((r) => setTimeout(r, 300));
await page.evaluate(() => {
  const btns = [...document.querySelectorAll("button.registry-home__facet")];
  btns.find((b) => b.textContent.trim() === "specials")?.click();
});
await new Promise((r) => setTimeout(r, 400));
const afterFacet = await page.$eval(
  "#registry-agent-results",
  (el) => el.textContent,
);
console.log("afterFacet", afterFacet);

await page.evaluate(() => {
  const btns = [...document.querySelectorAll("button")];
  btns.find((b) => b.textContent.trim() === "Graph viz")?.click();
});
await new Promise((r) => setTimeout(r, 400));
const graph = await page.$('[data-registry-view="graph"]');
console.log("graphPresent", Boolean(graph));

const okSearch = /Showing\s+1\s+of\s+133/.test(afterSearch || "");
const okTable = tableView === "table";
const okFacet = /Showing\s+19\s+of\s+133/.test(afterFacet || "");
const okGraph = Boolean(graph);
console.log(
  JSON.stringify({ okSearch, okTable, okFacet, okGraph, pass: okSearch && okTable && okFacet && okGraph }),
);

await browser.close();
process.exit(okSearch && okTable && okFacet && okGraph ? 0 : 1);
