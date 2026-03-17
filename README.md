# Multiplayer Browser Game (Node + React)

This repository now includes a browser-based multiplayer space game prototype:

- `server/`: Node.js + Express + Socket.IO backend
- `client/`: React + Vite frontend
- Room-based multiplayer join flow (`name + room code`)
- Phaser-powered space scene inspired by the original Python mechanics
- Progression persistence via a swappable repository abstraction

## Why this structure

Progression storage is abstracted behind a repository interface:

- `ProgressionRepository` (contract)
- `LocalFileProgressionRepository` (current local JSON storage)
- `MongoProgressionRepository` (future extension point)

Switch storage drivers through environment variables without touching game logic.

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
- `Left mouse`: fire projectile cannon
- `Space`: brake
- `Tab`: toggle cargo panel
- `E` near station: open station dialogue
