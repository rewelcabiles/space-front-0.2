import { ProgressionRepository } from "./progressionRepository.js";

export class MongoProgressionRepository extends ProgressionRepository {
  constructor() {
    super();
    throw new Error(
      "MongoProgressionRepository is not wired yet. Set PERSISTENCE_DRIVER=local for now.",
    );
  }
}
