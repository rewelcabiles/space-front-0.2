import {
  isValidPlayerState,
  isValidProgress,
  normalizePlayerName,
  normalizeRoomCode,
} from "../validators.js";

const defaultProgress = () => ({ level: 1, experience: 0 });
const defaultState = () => ({
  x: 1200,
  y: 1200,
  rotation: 0,
  velocityX: 0,
  velocityY: 0,
  health: 100,
});

export const registerSocketHandlers = ({
  io,
  roomManager,
  progressionRepository,
}) => {
  io.on("connection", (socket) => {
    socket.on("join_room", async (payload = {}) => {
      const playerName = normalizePlayerName(payload.playerName);
      const roomCode = normalizeRoomCode(payload.roomCode);

      if (!playerName || !roomCode) {
        socket.emit("socket_error", {
          message: "Both player name and room code are required.",
        });
        return;
      }

      const savedProgress = await progressionRepository.getPlayerProgress(
        roomCode,
        playerName,
      );
      const progress = savedProgress ?? defaultProgress();

      socket.data.roomCode = roomCode;
      socket.data.playerName = playerName;

      await socket.join(roomCode);
      roomManager.addPlayer(roomCode, {
        socketId: socket.id,
        name: playerName,
        progress,
        state: defaultState(),
      });
      await progressionRepository.savePlayerProgress(roomCode, playerName, progress);

      socket.emit("joined_room", {
        roomCode,
        playerName,
        progress,
        state: roomManager.getPlayer(roomCode, socket.id)?.state ?? defaultState(),
      });
      io.to(roomCode).emit("room_state", roomManager.getRoomState(roomCode));
    });

    socket.on("progress_update", async (payload = {}) => {
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
    });

    socket.on("player_state_update", (payload = {}) => {
      const roomCode = socket.data.roomCode;
      if (!roomCode) {
        return;
      }

      if (!isValidPlayerState(payload.state)) {
        return;
      }

      const player = roomManager.updatePlayerState(roomCode, socket.id, payload.state);
      if (!player) {
        return;
      }

      socket.to(roomCode).emit("player_state", {
        socketId: socket.id,
        name: player.name,
        state: payload.state,
      });
    });

    socket.on("disconnect", () => {
      const roomCode = socket.data.roomCode;
      if (!roomCode) {
        return;
      }

      roomManager.removePlayer(roomCode, socket.id);
      io.to(roomCode).emit("room_state", roomManager.getRoomState(roomCode));
    });
  });
};
