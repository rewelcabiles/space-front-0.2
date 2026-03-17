import { useEffect, useRef } from "react";
import Phaser from "phaser";

import { SpacePortScene } from "./scenes/SpacePortScene";

export function SpaceGameCanvas({
  ownSocketId,
  roomCode,
  players,
  content,
  onStateUpdate,
  onProgressGain,
  onCargoChange,
  onHealthChange,
  onShipHudUpdate,
  onToggleCargo,
  onStationInteract,
}) {
  const containerRef = useRef(null);
  const playersRef = useRef(players);
  const roomCodeRef = useRef(roomCode);
  const onStateUpdateRef = useRef(onStateUpdate);
  const onProgressGainRef = useRef(onProgressGain);
  const onCargoChangeRef = useRef(onCargoChange);
  const onHealthChangeRef = useRef(onHealthChange);
  const onShipHudUpdateRef = useRef(onShipHudUpdate);
  const onToggleCargoRef = useRef(onToggleCargo);
  const onStationInteractRef = useRef(onStationInteract);

  useEffect(() => {
    playersRef.current = players;
  }, [players]);
  useEffect(() => {
    roomCodeRef.current = roomCode;
  }, [roomCode]);
  useEffect(() => {
    onStateUpdateRef.current = onStateUpdate;
  }, [onStateUpdate]);
  useEffect(() => {
    onProgressGainRef.current = onProgressGain;
  }, [onProgressGain]);
  useEffect(() => {
    onCargoChangeRef.current = onCargoChange;
  }, [onCargoChange]);
  useEffect(() => {
    onHealthChangeRef.current = onHealthChange;
  }, [onHealthChange]);
  useEffect(() => {
    onShipHudUpdateRef.current = onShipHudUpdate;
  }, [onShipHudUpdate]);
  useEffect(() => {
    onToggleCargoRef.current = onToggleCargo;
  }, [onToggleCargo]);
  useEffect(() => {
    onStationInteractRef.current = onStationInteract;
  }, [onStationInteract]);

  useEffect(() => {
    if (!containerRef.current || !ownSocketId) {
      return;
    }

    const scene = new SpacePortScene({
      hooks: {
        getOwnSocketId: () => ownSocketId,
        getRemotePlayers: () => playersRef.current,
        getRoomStats: () => ({
          roomCode: roomCodeRef.current,
          playerCount: playersRef.current.length,
        }),
        onStateUpdate: (...args) => onStateUpdateRef.current?.(...args),
        onProgressGain: (...args) => onProgressGainRef.current?.(...args),
        onCargoChange: (...args) => onCargoChangeRef.current?.(...args),
        onHealthChange: (...args) => onHealthChangeRef.current?.(...args),
        onShipHudUpdate: (...args) => onShipHudUpdateRef.current?.(...args),
        onToggleCargo: (...args) => onToggleCargoRef.current?.(...args),
        onStationInteract: (...args) => onStationInteractRef.current?.(...args),
      },
      content,
    });

    const game = new Phaser.Game({
      type: Phaser.AUTO,
      parent: containerRef.current,
      width: window.innerWidth,
      height: window.innerHeight,
      backgroundColor: "#020617",
      physics: {
        default: "arcade",
        arcade: {
          gravity: { y: 0 },
          debug: false,
        },
      },
      scene: [scene],
      scale: {
        mode: Phaser.Scale.RESIZE,
        autoCenter: Phaser.Scale.NO_CENTER,
      },
      render: {
        antialias: true,
      },
    });

    return () => {
      game.destroy(true);
    };
  }, [content, ownSocketId]);

  return <div className="game-canvas" ref={containerRef} />;
}
