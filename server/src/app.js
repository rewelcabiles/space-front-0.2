import { createServer } from "node:http";

import cors from "cors";
import express from "express";
import { Server } from "socket.io";

import { createApiRouter } from "./http/createApiRouter.js";
import { createProgressionRepository } from "./persistence/createProgressionRepository.js";
import { RoomManager } from "./rooms/roomManager.js";
import { registerSocketHandlers } from "./socket/registerSocketHandlers.js";

export const buildApplication = ({
  progressionRepository = createProgressionRepository(),
  roomManager = new RoomManager(),
} = {}) => {
  const app = express();
  app.use(cors());
  app.use(express.json());
  app.use("/api", createApiRouter({ roomManager }));

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
