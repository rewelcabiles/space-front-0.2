export class RoomManager {
  constructor() {
    this.rooms = new Map();
  }

  getRoom(roomCode) {
    if (!this.rooms.has(roomCode)) {
      this.rooms.set(roomCode, new Map());
    }

    return this.rooms.get(roomCode);
  }

  addPlayer(roomCode, player) {
    const room = this.getRoom(roomCode);
    room.set(player.socketId, player);
    return this.getRoomState(roomCode);
  }

  removePlayer(roomCode, socketId) {
    const room = this.rooms.get(roomCode);
    if (!room) {
      return null;
    }

    room.delete(socketId);

    if (room.size === 0) {
      this.rooms.delete(roomCode);
      return { roomCode, players: [] };
    }

    return this.getRoomState(roomCode);
  }

  getPlayer(roomCode, socketId) {
    return this.rooms.get(roomCode)?.get(socketId) ?? null;
  }

  updatePlayerProgress(roomCode, socketId, progress) {
    const room = this.rooms.get(roomCode);
    if (!room) {
      return null;
    }

    const player = room.get(socketId);
    if (!player) {
      return null;
    }

    player.progress = progress;
    room.set(socketId, player);
    return this.getRoomState(roomCode);
  }

  getRoomState(roomCode) {
    const room = this.rooms.get(roomCode);
    if (!room) {
      return { roomCode, players: [] };
    }

    return {
      roomCode,
      players: [...room.values()].map(({ socketId, name, progress }) => ({
        socketId,
        name,
        progress,
      })),
    };
  }
}
