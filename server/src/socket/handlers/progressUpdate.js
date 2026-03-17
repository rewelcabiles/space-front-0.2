import { isValidProgress } from "../../validators.js";

export const createProgressUpdateHandler = ({
  roomManager,
  progressionRepository,
  io,
  socket,
}) =>
  async (payload = {}) => {
    const roomCode = socket.data.roomCode;
    const playerName = socket.data.playerName;

    if (!roomCode || !playerName) {
      socket.emit("socket_error", { message: "Join a room first." });
      return;
    }

    if (!isValidProgress(payload.progress)) {
      socket.emit("socket_error", {
        message: "Progress update is invalid.",
      });
      return;
    }

    roomManager.updatePlayerProgress(roomCode, socket.id, payload.progress);
    await progressionRepository.savePlayerProgress(
      roomCode,
      playerName,
      payload.progress,
    );
    io.to(roomCode).emit("room_state", roomManager.getRoomState(roomCode));
  };
