import { createServer } from "node:http";

import cors from "cors";
import express from "express";
import { Server } from "socket.io";

import { createProgressionRepository } from "./persistence/createProgressionRepository.js";
import { RoomManager } from "./rooms/roomManager.js";
import { registerSocketHandlers } from "./socket/registerSocketHandlers.js";
import { normalizeRoomCode } from "./validators.js";

export const buildApplication = ({
  progressionRepository = createProgressionRepository(),
  roomManager = new RoomManager(),
} = {}) => {
  const app = express();
  app.use(cors());
  app.use(express.json());

  app.get("/api/health", (_request, response) => {
    response.json({ status: "ok" });
  });

  app.get("/api/rooms/:roomCode", (request, response) => {
    const roomCode = normalizeRoomCode(request.params.roomCode);
    response.json(roomManager.getRoomState(roomCode));
  });

  const httpServer = createServer(app);
  const io = new Server(httpServer, {
    cors: {
      origin: "*",
    },
  });

  registerSocketHandlers({
    io,
    roomManager,
    progressionRepository,
  });

  return {
    app,
    httpServer,
    io,
    roomManager,
    progressionRepository,
  };
};
