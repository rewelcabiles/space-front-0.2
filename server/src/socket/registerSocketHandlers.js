import { createDisconnectHandler } from "./handlers/disconnect.js";
import { createJoinRoomHandler } from "./handlers/joinRoom.js";
import { createPlayerStateUpdateHandler } from "./handlers/playerStateUpdate.js";
import { createProgressUpdateHandler } from "./handlers/progressUpdate.js";

export const registerSocketHandlers = ({
  io,
  roomManager,
  progressionRepository,
}) => {
  io.on("connection", (socket) => {
    socket.on(
      "join_room",
      createJoinRoomHandler({ io, roomManager, progressionRepository, socket }),
    );
    socket.on(
      "progress_update",
      createProgressUpdateHandler({ io, roomManager, progressionRepository, socket }),
    );
    socket.on(
      "player_state_update",
      createPlayerStateUpdateHandler({ roomManager, socket }),
    );
    socket.on("disconnect", createDisconnectHandler({ io, roomManager, socket }));
  });
};
