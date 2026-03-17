import { useState } from "react";

import { CargoPanel } from "./components/CargoPanel";
import { JoinRoomForm } from "./components/JoinRoomForm";
import { PlayersPanel } from "./components/PlayersPanel";
import { StationDialog } from "./components/StationDialog";
import { useRoomConnection } from "./hooks/useRoomConnection";
import { useGameContent } from "./game/content/useGameContent";
import { SpaceGameCanvas } from "./game/SpaceGameCanvas";
import "./App.css";

function App() {
  const [cargo, setCargo] = useState({});
  const [showCargo, setShowCargo] = useState(true);
  const [dialogNodeId, setDialogNodeId] = useState(null);
  const room = useRoomConnection();
  const content = useGameContent(room.serverUrl);

  const handleJoin = (event) => {
    setCargo({});
    setDialogNodeId(null);
    room.connectAndJoin(event);
  };

  const handleLeave = () => {
    room.leaveRoom();
    setCargo({});
    setDialogNodeId(null);
  };

  return (
    <main className="layout">
      <section className="card">
        <h1>Multiplayer Browser Game</h1>
        <p className="subtitle">
          Original Python space game ported to browser with modular Node + React architecture.
        </p>

        {!room.joined && (
          <JoinRoomForm
            playerName={room.playerName}
            roomCode={room.roomCode}
            onChangePlayerName={room.setPlayerName}
            onChangeRoomCode={room.setRoomCode}
            onSubmit={handleJoin}
          />
        )}

        {room.joined && (
          <div className="in-room">
            <div className="room-header">
              <h2>Room {room.roomState.roomCode || room.roomCode}</h2>
              <button type="button" className="ghost" onClick={handleLeave}>
                Leave
              </button>
            </div>

            <div className="progress-panel">
              <p><strong>{room.playerName}</strong></p>
              <p>Hull: {room.health}/100</p>
              <p>Level {room.myProgress.level} ({room.myProgress.experience}/100 XP)</p>
              <button type="button" onClick={() => setShowCargo((value) => !value)}>
                {showCargo ? "Hide cargo" : "Show cargo"}
              </button>
              <button
                type="button"
                className="ghost"
                onClick={() => setDialogNodeId(content.stationRootId)}
              >
                Open station
              </button>
            </div>

            <SpaceGameCanvas
              ownSocketId={room.ownSocketId}
              roomCode={room.roomState.roomCode || room.roomCode}
              players={room.roomState.players}
              content={content}
              onStateUpdate={room.sendStateUpdate}
              onProgressGain={room.emitProgressGain}
              onCargoChange={setCargo}
              onHealthChange={room.setHealth}
              onToggleCargo={() => setShowCargo((value) => !value)}
              onStationInteract={() => {
                setDialogNodeId((nodeId) => (nodeId ? null : content.stationRootId));
              }}
            />

            <div className="panels">
              <PlayersPanel players={room.roomState.players} />

              {showCargo && <CargoPanel cargo={cargo} />}
            </div>
          </div>
        )}

        {room.errorMessage && <p className="error">{room.errorMessage}</p>}
      </section>

      {dialogNodeId && (
        <StationDialog
          dialogueMap={content.stationDialogue}
          nodeId={dialogNodeId}
          onSelectNode={(nextNodeId) => {
            setDialogNodeId(nextNodeId ?? null);
          }}
        />
      )}
    </main>
  );
}

export default App;
