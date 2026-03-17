import { Router } from "express";

import { readGameContent } from "./gameContentService.js";
import { normalizeRoomCode } from "../validators.js";

export const createApiRouter = ({ roomManager }) => {
  const router = Router();

  router.get("/health", (_request, response) => {
    response.json({ status: "ok" });
  });

  router.get("/rooms/:roomCode", (request, response) => {
    const roomCode = normalizeRoomCode(request.params.roomCode);
    response.json(roomManager.getRoomState(roomCode));
  });

  router.get("/game-content", async (_request, response, next) => {
    try {
      const content = await readGameContent();
      response.json(content);
    } catch (error) {
      next(error);
    }
  });

  return router;
};
