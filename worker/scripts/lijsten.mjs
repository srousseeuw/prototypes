// Zet wedstrijden/selectie.json om naar een JS-module, zodat de Worker geen
// JSON-import nodig heeft (en de code gewoon onder node te testen valt).
// Draai dit na elke wijziging aan selectie.json:  npm run lijsten
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const hier = dirname(fileURLToPath(import.meta.url));
const bron = join(hier, "..", "..", "wedstrijden", "selectie.json");
const doel = join(hier, "..", "src", "lijsten.js");

const lijsten = JSON.parse(readFileSync(bron, "utf-8"));
delete lijsten._uitleg;

writeFileSync(doel,
  "// GEGENEREERD — niet met de hand bewerken.\n" +
  "// Bron: wedstrijden/selectie.json  ·  opnieuw maken: npm run lijsten\n" +
  "export default " + JSON.stringify(lijsten, null, 2) + ";\n", "utf-8");

console.log(`✓ ${doel} bijgewerkt (${Object.keys(lijsten.categorieen).length} categorieën)`);
