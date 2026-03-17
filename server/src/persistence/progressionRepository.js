export class ProgressionRepository {
  async getPlayerProgress(_roomCode, _playerName) {
    throw new Error("getPlayerProgress must be implemented.");
  }

  async savePlayerProgress(_roomCode, _playerName, _progress) {
    throw new Error("savePlayerProgress must be implemented.");
  }
}
