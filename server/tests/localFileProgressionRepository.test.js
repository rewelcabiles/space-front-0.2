import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { LocalFileProgressionRepository } from "../src/persistence/localFileProgressionRepository.js";

let tempDirectory = null;

afterEach(async () => {
  if (tempDirectory) {
    await rm(tempDirectory, { recursive: true, force: true });
    tempDirectory = null;
  }
});

describe("LocalFileProgressionRepository", () => {
  it("persists and reloads progression by room and player", async () => {
    tempDirectory = await mkdtemp(join(tmpdir(), "progression-repo-"));
    const storagePath = join(tempDirectory, "progression.json");

    const repository = new LocalFileProgressionRepository(storagePath);
    await repository.savePlayerProgress("ABCD", "Alice", { level: 2, experience: 40 });
    await repository.savePlayerProgress("ABCD", "Bob", { level: 5, experience: 10 });

    const aliceProgress = await repository.getPlayerProgress("ABCD", "Alice");
    const bobProgress = await repository.getPlayerProgress("ABCD", "Bob");
    const unknownProgress = await repository.getPlayerProgress("ABCD", "Charlie");

    expect(aliceProgress).toEqual({ level: 2, experience: 40 });
    expect(bobProgress).toEqual({ level: 5, experience: 10 });
    expect(unknownProgress).toBeNull();
  });
});
