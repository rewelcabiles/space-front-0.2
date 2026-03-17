import { useEffect, useMemo, useRef, useState } from "react";
import { io } from "socket.io-client";
import "./App.css";

const buildNextProgress = (currentProgress) => {
  let level = currentProgress.level;
  let experience = currentProgress.experience + 10;

  while (experience >= 100) {
    experience -= 100;
    level += 1;
  }

  return { level, experience };
};

function App() {
  const [playerName, setPlayerName] = useState("");
  const [roomCode, setRoomCode] = useState("");
  const [roomState, setRoomState] = useState({ roomCode: "", players: [] });
  const [myProgress, setMyProgress] = useState({ level: 1, experience: 0 });
  const [joined, setJoined] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const socketRef = useRef(null);

  const serverUrl = useMemo(
    () => import.meta.env.VITE_SERVER_URL ?? "http://localhost:3001",
    [],
  );

  useEffect(() => {
    return () => {
      socketRef.current?.disconnect();
    };
  }, []);

  const connectAndJoin = (event) => {
    event.preventDefault();
    setErrorMessage("");

    const trimmedName = playerName.trim();
    const normalizedRoomCode = roomCode.trim().toUpperCase();
    if (!trimmedName || !normalizedRoomCode) {
      setErrorMessage("Please provide both a name and room code.");
      return;
    }

    socketRef.current?.disconnect();
    const socket = io(serverUrl, { transports: ["websocket"] });
    socketRef.current = socket;

    socket.on("joined_room", (payload) => {
      setJoined(true);
      setRoomCode(payload.roomCode);
      setPlayerName(payload.playerName);
      setMyProgress(payload.progress);
    });

    socket.on("room_state", (payload) => {
      setRoomState(payload);
    });

    socket.on("socket_error", (payload) => {
      setErrorMessage(payload.message ?? "Unknown socket error.");
    });

    socket.on("connect_error", () => {
      setErrorMessage("Cannot reach server. Ensure backend runs on port 3001.");
    });

    socket.on("connect", () => {
      socket.emit("join_room", {
        playerName: trimmedName,
        roomCode: normalizedRoomCode,
      });
    });
  };

  const updateProgress = () => {
    if (!socketRef.current?.connected) {
      setErrorMessage("Socket disconnected. Join a room again.");
      return;
    }

    const nextProgress = buildNextProgress(myProgress);
    setMyProgress(nextProgress);
    socketRef.current.emit("progress_update", { progress: nextProgress });
  };

  const leaveRoom = () => {
    socketRef.current?.disconnect();
    socketRef.current = null;
    setJoined(false);
    setRoomState({ roomCode: "", players: [] });
    setMyProgress({ level: 1, experience: 0 });
    setErrorMessage("");
  };

  return (
    <main className="layout">
      <section className="card">
        <h1>Multiplayer Browser Game</h1>
        <p className="subtitle">
          Join with your name and room code. Progress syncs live across players.
        </p>

        {!joined && (
          <form className="join-form" onSubmit={connectAndJoin}>
            <label>
              Player name
              <input
                value={playerName}
                onChange={(event) => setPlayerName(event.target.value)}
                placeholder="ex: NovaPilot"
              />
            </label>

            <label>
              Room code
              <input
                value={roomCode}
                onChange={(event) => setRoomCode(event.target.value)}
                placeholder="ex: ALFA"
              />
            </label>

            <button type="submit">Join room</button>
          </form>
        )}

        {joined && (
          <div className="in-room">
            <div className="room-header">
              <h2>Room {roomState.roomCode || roomCode}</h2>
              <button type="button" className="ghost" onClick={leaveRoom}>
                Leave
              </button>
            </div>

            <div className="progress-panel">
              <p>
                <strong>{playerName}</strong> - Level {myProgress.level} (
                {myProgress.experience}/100 XP)
              </p>
              <button type="button" onClick={updateProgress}>
                Gain 10 XP
              </button>
            </div>

            <h3>Players in room</h3>
            <ul className="players">
              {roomState.players.map((player) => (
                <li key={player.socketId}>
                  <span>{player.name}</span>
                  <span>
                    L{player.progress.level} - {player.progress.experience} XP
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {errorMessage && <p className="error">{errorMessage}</p>}
      </section>
    </main>
  );
}

export default App;
