import { buildApplication } from "./app.js";

const port = Number(process.env.PORT ?? "3001");

const { httpServer } = buildApplication();

httpServer.listen(port, () => {
  console.log(`Multiplayer server running on http://localhost:${port}`);
});
