import { fileURLToPath } from "node:url";

import { LocalFileProgressionRepository } from "./localFileProgressionRepository.js";
import { MongoProgressionRepository } from "./mongoProgressionRepository.js";

const defaultLocalStorePath = fileURLToPath(
  new URL("../../data/progression.json", import.meta.url),
);

export const createProgressionRepository = ({
  driver = process.env.PERSISTENCE_DRIVER ?? "local",
  localFilePath = process.env.LOCAL_PROGRESS_FILE ?? defaultLocalStorePath,
} = {}) => {
  if (driver === "mongo") {
    return new MongoProgressionRepository();
  }

  return new LocalFileProgressionRepository(localFilePath);
};
