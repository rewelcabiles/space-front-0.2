import { normalizePlayerName, normalizeRoomCode } from "../../validators.js";
import { defaultProgress, defaultState } from "../defaultState.js";

export const createJoinRoomHandler = ({
  roomManager,
  progressionRepository,
  io,
  socket,
}) =>
  async (payload = {}) => {
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
  };
