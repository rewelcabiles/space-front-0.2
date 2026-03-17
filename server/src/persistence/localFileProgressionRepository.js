import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname } from "node:path";

import { ProgressionRepository } from "./progressionRepository.js";

const makeKey = (roomCode, playerName) =>
  `${roomCode.toUpperCase()}:${playerName.trim().toLowerCase()}`;

export class LocalFileProgressionRepository extends ProgressionRepository {
  constructor(storageFilePath) {
    super();
    this.storageFilePath = storageFilePath;
  }

  async ensureStoreExists() {
    await mkdir(dirname(this.storageFilePath), { recursive: true });

    try {
      await readFile(this.storageFilePath, "utf8");
    } catch (error) {
      if (error.code === "ENOENT") {
        await writeFile(this.storageFilePath, JSON.stringify({}, null, 2), "utf8");
        return;
      }

      throw error;
    }
  }

  async readStore() {
    await this.ensureStoreExists();
    const content = await readFile(this.storageFilePath, "utf8");
    return JSON.parse(content || "{}");
  }

  async writeStore(data) {
    await writeFile(this.storageFilePath, JSON.stringify(data, null, 2), "utf8");
  }

  async getPlayerProgress(roomCode, playerName) {
    const store = await this.readStore();
    const key = makeKey(roomCode, playerName);
    return store[key] ?? null;
  }

  async savePlayerProgress(roomCode, playerName, progress) {
    const store = await this.readStore();
    const key = makeKey(roomCode, playerName);
    store[key] = progress;
    await this.writeStore(store);
    return progress;
  }
}
