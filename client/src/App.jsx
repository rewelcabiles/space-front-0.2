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

  if (!room.joined) {
    return (
      <main className="lobby-layout">
        <section className="lobby-panel">
          <JoinRoomForm
            playerName={room.playerName}
            roomCode={room.roomCode}
            onChangePlayerName={room.setPlayerName}
            onChangeRoomCode={room.setRoomCode}
            onSubmit={handleJoin}
          />
          {room.errorMessage && <p className="error">{room.errorMessage}</p>}
        </section>
      </main>
    );
  }

  return (
    <main className="immersive-layout">
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

      <section className="floating-topbar">
        <div className="pill">{room.roomState.roomCode || room.roomCode}</div>
        <div className="pill">{room.playerName}</div>
        <div className="pill">Hull {room.health}/100</div>
        <div className="pill">
          Lv {room.myProgress.level} - {room.myProgress.experience}/100 XP
        </div>
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
        <button type="button" className="ghost" onClick={handleLeave}>
          Leave
        </button>
      </section>

      <section className="floating-right-panel">
        <PlayersPanel players={room.roomState.players} />
        {showCargo && <CargoPanel cargo={cargo} />}
      </section>

      {room.errorMessage && <p className="floating-error">{room.errorMessage}</p>}

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
