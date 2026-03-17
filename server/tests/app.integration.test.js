import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import request from "supertest";
import { io as createClient } from "socket.io-client";
import { afterEach, describe, expect, it } from "vitest";

import { buildApplication } from "../src/app.js";
import { LocalFileProgressionRepository } from "../src/persistence/localFileProgressionRepository.js";

const waitForSocketEvent = (socket, eventName, timeoutMs = 3000) =>
  new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error(`Timed out waiting for ${eventName}`));
    }, timeoutMs);

    socket.once(eventName, (payload) => {
      clearTimeout(timer);
      resolve(payload);
    });
  });

let tempDirectory = null;

afterEach(async () => {
  if (tempDirectory) {
    await rm(tempDirectory, { recursive: true, force: true });
    tempDirectory = null;
  }
});

describe("multiplayer app", () => {
  it("serves a health endpoint", async () => {
    const { app } = buildApplication();
    const response = await request(app).get("/api/health");
    expect(response.statusCode).toBe(200);
    expect(response.body).toEqual({ status: "ok" });
  });

  it("syncs room state and restores saved progression on rejoin", async () => {
    tempDirectory = await mkdtemp(join(tmpdir(), "multiplayer-server-"));
    const storagePath = join(tempDirectory, "progression.json");
    const progressionRepository = new LocalFileProgressionRepository(storagePath);
    const { httpServer } = buildApplication({ progressionRepository });
    await new Promise((resolve) => httpServer.listen(0, resolve));

    const { port } = httpServer.address();
    const serverUrl = `http://127.0.0.1:${port}`;
    const roomCode = "ALFA";
    const clients = [];

    try {
      const alice = createClient(serverUrl, { transports: ["websocket"] });
      clients.push(alice);
      await waitForSocketEvent(alice, "connect");

      const initialRoomStatePromise = waitForSocketEvent(alice, "room_state");
      alice.emit("join_room", { playerName: "Alice", roomCode });
      await waitForSocketEvent(alice, "joined_room");
      const initialRoomState = await initialRoomStatePromise;
      expect(initialRoomState.players).toHaveLength(1);

      const bob = createClient(serverUrl, { transports: ["websocket"] });
      clients.push(bob);
      await waitForSocketEvent(bob, "connect");

      const twoPlayerRoomStatePromise = waitForSocketEvent(bob, "room_state");
      bob.emit("join_room", { playerName: "Bob", roomCode });
      await waitForSocketEvent(bob, "joined_room");
      const twoPlayerRoomState = await twoPlayerRoomStatePromise;
      expect(twoPlayerRoomState.players).toHaveLength(2);

      const syncedStatePromise = waitForSocketEvent(bob, "room_state");
      alice.emit("progress_update", {
        progress: { level: 3, experience: 85 },
      });
      const syncedState = await syncedStatePromise;
      const syncedAlice = syncedState.players.find((player) => player.name === "Alice");
      expect(syncedAlice.progress).toEqual({ level: 3, experience: 85 });

      const stateAfterDisconnectPromise = waitForSocketEvent(bob, "room_state");
      alice.disconnect();
      const afterDisconnectState = await stateAfterDisconnectPromise;
      expect(afterDisconnectState.players).toHaveLength(1);
      expect(afterDisconnectState.players[0].name).toBe("Bob");

      const returningAlice = createClient(serverUrl, { transports: ["websocket"] });
      clients.push(returningAlice);
      await waitForSocketEvent(returningAlice, "connect");

      const rejoinRoomStatePromise = waitForSocketEvent(returningAlice, "room_state");
      returningAlice.emit("join_room", { playerName: "Alice", roomCode });
      const rejoinPayload = await waitForSocketEvent(returningAlice, "joined_room");
      expect(rejoinPayload.progress).toEqual({ level: 3, experience: 85 });
      await rejoinRoomStatePromise;
    } finally {
      clients.forEach((client) => {
        if (client.connected) {
          client.disconnect();
        }
      });

      await new Promise((resolve, reject) => {
        httpServer.close((error) => (error ? reject(error) : resolve()));
      });
    }
  });
});
