import { isValidPlayerState } from "../../validators.js";

export const createPlayerStateUpdateHandler = ({ roomManager, socket }) =>
  (payload = {}) => {
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
  };
