# Multiplayer Browser Game (Node + React)

This repository now includes a browser-based multiplayer space game prototype:

- `server/`: Node.js + Express + Socket.IO backend
- `client/`: React + Vite frontend
- Room-based multiplayer join flow (`name + room code`)
- Phaser-powered space scene inspired by the original Python mechanics
- Original game content loaded from Python JSON assets (`ships/modules/items/dialogue`)
- Sprite assets aligned to original names (`nem-1`, `asteroid_1`, `space_station_1`, `rock_drop_1`)
- Progression persistence via a swappable repository abstraction

## Why this structure

Progression storage is abstracted behind a repository interface:

- `ProgressionRepository` (contract)
- `LocalFileProgressionRepository` (current local JSON storage)
- `MongoProgressionRepository` (future extension point)

Switch storage drivers through environment variables without touching game logic.

Backend and frontend are now split into modular layers instead of monolithic files:

- Backend:
  - HTTP router modules in `server/src/http/`
  - Socket event handlers in `server/src/socket/handlers/`
  - Shared room/persistence/domain services in dedicated directories
- Frontend:
  - Socket/session state hook in `client/src/hooks/`
  - Game scene in `client/src/game/scenes/`
  - React canvas wrapper in `client/src/game/SpaceGameCanvas.jsx`
  - UI components in `client/src/components/`
  - Dialogue/content utilities in `client/src/game/content/` and `client/src/game/dialogue.js`

## Quick start

From repo root:

1. Install root tools:
   - `npm install`
2. Install backend dependencies:
   - `cd server && npm install`
3. Install frontend dependencies:
   - `cd ../client && npm install`
4. Run both apps:
   - `cd .. && npm run dev`

Frontend runs on Vite default (`http://localhost:5173`) and backend on `http://localhost:3001`.

## Backend environment variables

- `PORT` (default: `3001`)
- `PERSISTENCE_DRIVER` (`local` or `mongo`, default: `local`)
- `LOCAL_PROGRESS_FILE` (default: `server/data/progression.json`)

## HTTP API endpoints

- `GET /api/health`
- `GET /api/rooms/:roomCode`
- `GET /api/game-content` (ships/modules/items/dialogue payload from original Python data files)

## Socket events

- Client -> server:
  - `join_room` `{ playerName, roomCode }`
  - `progress_update` `{ progress: { level, experience } }`
  - `player_state_update` `{ state: { x, y, rotation, velocityX, velocityY, health } }`
- Server -> client:
  - `joined_room`
  - `room_state`
  - `player_state`
  - `socket_error`

## In-game controls

- `W/A/S/D`: move ship
- `Mouse`: aim ship
- `Left mouse` or `F`: fire projectile cannon
- `Space`: brake
- `Tab`: toggle cargo panel
- `E` near station: open station dialogue
