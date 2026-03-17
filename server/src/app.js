import { createServer } from "node:http";
import fs from "node:fs";

import cors from "cors";
import express from "express";
import { Server } from "socket.io";

import { createProgressionRepository } from "./persistence/createProgressionRepository.js";
import { RoomManager } from "./rooms/roomManager.js";
import { registerSocketHandlers } from "./socket/registerSocketHandlers.js";
import { normalizeRoomCode } from "./validators.js";

const DEBUG_LOG_PATH = "/opt/cursor/logs/debug.log";

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

  app.post("/api/debug-log", (request, response) => {
    const incoming = request.body ?? {};
    const payload = {
      hypothesisId: incoming.hypothesisId ?? "unknown",
      location: incoming.location ?? "unknown",
      message: incoming.message ?? "",
      data: typeof incoming.data === "object" && incoming.data ? incoming.data : {},
      timestamp: Number.isFinite(incoming.timestamp) ? incoming.timestamp : Date.now(),
    };
    try {
      fs.appendFileSync(`${DEBUG_LOG_PATH}`, `${JSON.stringify(payload)}\n`);
    } catch (_error) {
      // swallow logging errors to avoid affecting gameplay
    }
    response.status(204).end();
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
