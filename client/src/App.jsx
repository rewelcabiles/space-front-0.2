import { useEffect, useMemo, useRef, useState } from "react";
import { io } from "socket.io-client";

import { SpaceGame } from "./game/SpaceGame";
import { STATION_DIALOG } from "./game/gameData";
import "./App.css";

const applyXpGain = (currentProgress, xpGain) => {
  let level = currentProgress.level;
  let experience = currentProgress.experience + xpGain;

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
  const [ownSocketId, setOwnSocketId] = useState("");
  const [health, setHealth] = useState(100);
  const [cargo, setCargo] = useState({});
  const [showCargo, setShowCargo] = useState(true);
  const [dialogNodeId, setDialogNodeId] = useState(null);
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
      setOwnSocketId(socket.id);
      setHealth(payload.state?.health ?? 100);
      setCargo({});
      setDialogNodeId(null);
    });

    socket.on("room_state", (payload) => {
      setRoomState(payload);
    });

    socket.on("player_state", (payload) => {
      setRoomState((previous) => ({
        ...previous,
        players: previous.players.map((player) =>
          player.socketId === payload.socketId
            ? { ...player, state: payload.state }
            : player
        ),
      }));
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

  const emitProgressGain = (xpGain) => {
    if (!socketRef.current?.connected) {
      setErrorMessage("Socket disconnected. Join a room again.");
      return;
    }

    setMyProgress((previous) => {
      const nextProgress = applyXpGain(previous, xpGain);
      socketRef.current?.emit("progress_update", { progress: nextProgress });
      return nextProgress;
    });
  };

  const leaveRoom = () => {
    socketRef.current?.disconnect();
    socketRef.current = null;
    setJoined(false);
    setOwnSocketId("");
    setRoomState({ roomCode: "", players: [] });
    setMyProgress({ level: 1, experience: 0 });
    setCargo({});
    setDialogNodeId(null);
    setErrorMessage("");
  };

  const currentDialogNode = dialogNodeId ? STATION_DIALOG[dialogNodeId] : null;

  return (
    <main className="layout">
      <section className="card">
        <h1>Multiplayer Browser Game</h1>
        <p className="subtitle">
          Python space prototype rebuilt for browser multiplayer.
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
              <p><strong>{playerName}</strong></p>
              <p>Hull: {health}/100</p>
              <p>Level {myProgress.level} ({myProgress.experience}/100 XP)</p>
              <button type="button" onClick={() => setShowCargo((value) => !value)}>
                {showCargo ? "Hide cargo" : "Show cargo"}
              </button>
              <button type="button" className="ghost" onClick={() => setDialogNodeId("intro-1")}>
                Open station
              </button>
            </div>

            <SpaceGame
              ownSocketId={ownSocketId}
              roomCode={roomState.roomCode || roomCode}
              players={roomState.players}
              onStateUpdate={(state) => {
                socketRef.current?.emit("player_state_update", { state });
              }}
              onProgressGain={emitProgressGain}
              onCargoChange={setCargo}
              onHealthChange={setHealth}
              onToggleCargo={() => setShowCargo((value) => !value)}
              onStationInteract={() => {
                setDialogNodeId((nodeId) => (nodeId ? null : "intro-1"));
              }}
            />

            <div className="panels">
              <section className="panel">
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
              </section>

              {showCargo && (
                <section className="panel">
                  <h3>Cargo</h3>
                  <ul className="cargo-list">
                    {Object.keys(cargo).length === 0 && <li>Empty hold</li>}
                    {Object.entries(cargo).map(([item, amount]) => (
                      <li key={item}>
                        <span>{item}</span>
                        <span>x{amount}</span>
                      </li>
                    ))}
                  </ul>
                </section>
              )}
            </div>
          </div>
        )}

        {errorMessage && <p className="error">{errorMessage}</p>}
      </section>

      {currentDialogNode && (
        <section className="dialog-overlay">
          <div className="dialog-card">
            {currentDialogNode.actor && <p className="dialog-actor">{currentDialogNode.actor}</p>}
            <h3>{currentDialogNode.title}</h3>
            {currentDialogNode.body && <p>{currentDialogNode.body}</p>}

            {currentDialogNode.type === "text" && currentDialogNode.next && (
              <button
                type="button"
                onClick={() => {
                  if (currentDialogNode.next === "exit") {
                    setDialogNodeId(null);
                    return;
                  }
                  setDialogNodeId(currentDialogNode.next);
                }}
              >
                Continue
              </button>
            )}

            {currentDialogNode.type === "choice" && (
              <div className="dialog-options">
                {currentDialogNode.options.map((option) => (
                  <button
                    key={option.text}
                    type="button"
                    onClick={() => {
                      if (option.next === "exit") {
                        setDialogNodeId(null);
                        return;
                      }
                      setDialogNodeId(option.next);
                    }}
                  >
                    {option.text}
                  </button>
                ))}
              </div>
            )}
          </div>
        </section>
      )}
    </main>
  );
}

export default App;
