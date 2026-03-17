export const createDisconnectHandler = ({ roomManager, io, socket }) => () => {
  const roomCode = socket.data.roomCode;
  if (!roomCode) {
    return;
  }

  roomManager.removePlayer(roomCode, socket.id);
  io.to(roomCode).emit("room_state", roomManager.getRoomState(roomCode));
};
