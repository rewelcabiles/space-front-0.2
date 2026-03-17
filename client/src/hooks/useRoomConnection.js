import { useEffect, useMemo, useRef, useState } from "react";
import { io } from "socket.io-client";

const applyXpGain = (currentProgress, xpGain) => {
  let level = currentProgress.level;
  let experience = currentProgress.experience + xpGain;

  while (experience >= 100) {
    experience -= 100;
    level += 1;
  }

  return { level, experience };
};

export const useRoomConnection = () => {
  const [playerName, setPlayerName] = useState("");
  const [roomCode, setRoomCode] = useState("");
  const [roomState, setRoomState] = useState({ roomCode: "", players: [] });
  const [myProgress, setMyProgress] = useState({ level: 1, experience: 0 });
  const [ownSocketId, setOwnSocketId] = useState("");
  const [health, setHealth] = useState(100);
  const [joined, setJoined] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const socketRef = useRef(null);
  const serverUrl = useMemo(
    () => import.meta.env.VITE_SERVER_URL ?? "http://localhost:3001",
    [],
  );

  useEffect(() => () => socketRef.current?.disconnect(), []);

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
    });

    socket.on("room_state", (payload) => {
      setRoomState(payload);
      const me = payload.players?.find((player) => player.socketId === socket.id);
      if (me?.progress) {
        setMyProgress(me.progress);
      }
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
    setMyProgress((previous) => {
      const nextProgress = applyXpGain(previous, xpGain);
      socketRef.current?.emit("progress_update", { progress: nextProgress });
      return nextProgress;
    });
  };

  const sendStateUpdate = (state) => {
    socketRef.current?.emit("player_state_update", { state });
  };

  const leaveRoom = () => {
    socketRef.current?.disconnect();
    socketRef.current = null;
    setJoined(false);
    setOwnSocketId("");
    setRoomState({ roomCode: "", players: [] });
    setMyProgress({ level: 1, experience: 0 });
    setHealth(100);
    setErrorMessage("");
  };

  return {
    serverUrl,
    socketRef,
    playerName,
    roomCode,
    roomState,
    myProgress,
    ownSocketId,
    health,
    joined,
    errorMessage,
    setPlayerName,
    setRoomCode,
    setHealth,
    connectAndJoin,
    emitProgressGain,
    sendStateUpdate,
    leaveRoom,
  };
};
