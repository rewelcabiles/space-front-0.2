import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const readJson = async (relativePath) => {
  const absolutePath = fileURLToPath(new URL(relativePath, import.meta.url));
  const fileContent = await readFile(absolutePath, "utf8");
  return JSON.parse(fileContent);
};

let cache = null;

export const readGameContent = async () => {
  if (cache) {
    return cache;
  }

  const [ships, modules, items, dialogue, stationDialogue] = await Promise.all([
    readJson("../../../data/ships.json"),
    readJson("../../../data/modules.json"),
    readJson("../../../data/items.json"),
    readJson("../../../data/dialogue.json"),
    readJson("../../../data/Space_Station_1.json"),
  ]);

  cache = {
    ships,
    modules,
    items,
    dialogue,
    stationDialogue,
  };

  return cache;
};
