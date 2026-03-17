import { useEffect, useRef } from "react";
import Phaser from "phaser";

import { LOOT_ITEMS, MODULES, SHIPS } from "./gameData";

const WORLD_SIZE = 2400;
const PLAYER_SPAWN = { x: WORLD_SIZE / 2, y: WORLD_SIZE / 2 };
const DEBUG_LOG_URL = `${import.meta.env.VITE_SERVER_URL ?? "http://localhost:3001"}/api/debug-log`;

const writeDebugLog = (payload) => {
  fetch(DEBUG_LOG_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...payload, timestamp: Date.now() }),
  }).catch(() => {});
};

const createTriangleTexture = (scene, key, color) => {
  if (scene.textures.exists(key)) {
    return;
  }

  const graphics = scene.add.graphics();
  graphics.fillStyle(color, 1);
  graphics.fillTriangle(32, 4, 6, 60, 58, 60);
  graphics.lineStyle(2, 0x0f172a, 1);
  graphics.strokeTriangle(32, 4, 6, 60, 58, 60);
  graphics.generateTexture(key, 64, 64);
  graphics.destroy();
};

const createCircleTexture = (scene, key, radius, color) => {
  if (scene.textures.exists(key)) {
    return;
  }

  const graphics = scene.add.graphics();
  graphics.fillStyle(color, 1);
  graphics.fillCircle(radius, radius, radius);
  graphics.generateTexture(key, radius * 2, radius * 2);
  graphics.destroy();
};

class SpacePortScene extends Phaser.Scene {
  constructor({ hooks, ownSocketId }) {
    super({ key: "space-port" });
    this.hooks = hooks;
    this.ownSocketId = ownSocketId;
    this.remoteShips = new Map();
    this.lastShipStateEmit = 0;
    this.lastCollisionDamage = 0;
    this.isNearStation = false;
  }

  preload() {}

  create() {
    createTriangleTexture(this, "ship-local", SHIPS["Nem-1"].color);
    createTriangleTexture(this, "ship-remote", 0xf59e0b);
    createCircleTexture(this, "projectile", 6, 0xf8fafc);
    createCircleTexture(this, "rock", 36, 0x64748b);
    createCircleTexture(this, "loot", 8, 0x22c55e);
    createCircleTexture(this, "station", 40, 0x38bdf8);

    this.cameras.main.setBackgroundColor("#020617");
    this.physics.world.setBounds(0, 0, WORLD_SIZE, WORLD_SIZE);

    this.drawBackgroundStars();

    this.player = this.physics.add.image(
      PLAYER_SPAWN.x,
      PLAYER_SPAWN.y,
      "ship-local",
    );
    this.player.setCollideWorldBounds(true);
    this.player.setDrag(280, 280);
    this.player.setMaxVelocity(SHIPS["Nem-1"].maxSpeed);
    this.playerHealth = 100;
    this.cargo = {};

    this.bullets = this.physics.add.group({
      classType: Phaser.Physics.Arcade.Image,
      maxSize: 120,
      runChildUpdate: false,
    });
    this.lastShotAt = 0;
    this.weaponStats = MODULES["Projectile Cannon Mk1"];

    this.rocks = this.physics.add.group({ immovable: true, allowGravity: false });
    this.spawnRocks(20);

    this.loot = this.physics.add.group({ allowGravity: false, immovable: true });
    this.station = this.physics.add.image(PLAYER_SPAWN.x - 140, PLAYER_SPAWN.y - 80, "station");
    this.station.setImmovable(true);
    this.station.body.moves = false;

    this.physics.add.overlap(this.player, this.loot, this.collectLoot, null, this);
    this.physics.add.overlap(this.bullets, this.rocks, this.hitRock, null, this);
    this.physics.add.collider(
      this.player,
      this.rocks,
      this.damageOnCollision,
      null,
      this,
    );

    this.keys = this.input.keyboard.addKeys("W,A,S,D,SPACE,TAB,E");
    this.input.keyboard.on("keydown-E", () => {
      if (this.isNearStation) {
        this.hooks.onStationInteract();
      }
    });
    this.input.keyboard.on("keydown-TAB", (event) => {
      event.preventDefault();
      this.hooks.onToggleCargo();
    });

    this.camera = this.cameras.main;
    this.camera.startFollow(this.player, true, 0.1, 0.1);
    this.camera.setBounds(0, 0, WORLD_SIZE, WORLD_SIZE);

    this.hudText = this.add
      .text(16, 16, "", { font: "16px monospace", fill: "#e2e8f0" })
      .setScrollFactor(0)
      .setDepth(50);
    this.promptText = this.add
      .text(16, 90, "", { font: "15px monospace", fill: "#93c5fd" })
      .setScrollFactor(0)
      .setDepth(50);

    this.minimap = this.add.graphics().setDepth(50).setScrollFactor(0);

    // #region agent log
    writeDebugLog({
      hypothesisId: "H2",
      location: "SpaceGame.jsx:create",
      message: "Scene created and rocks spawned",
      data: { rockCount: this.rocks.getChildren().length },
    });
    // #endregion
  }

  drawBackgroundStars() {
    const stars = this.add.graphics();
    stars.fillStyle(0xffffff, 0.55);

    for (let i = 0; i < 280; i += 1) {
      const x = Phaser.Math.Between(0, WORLD_SIZE);
      const y = Phaser.Math.Between(0, WORLD_SIZE);
      const radius = Phaser.Math.Between(1, 2);
      stars.fillCircle(x, y, radius);
    }
  }

  spawnRocks(count) {
    const starterRock = this.rocks.create(
      PLAYER_SPAWN.x + 110,
      PLAYER_SPAWN.y - 10,
      "rock",
    );
    starterRock.setCircle(36);
    starterRock.setData("hp", 10);
    starterRock.setData("maxHp", 10);

    for (let i = 0; i < count; i += 1) {
      const x = Phaser.Math.Between(140, WORLD_SIZE - 140);
      const y = Phaser.Math.Between(140, WORLD_SIZE - 140);
      const rock = this.rocks.create(x, y, "rock");
      rock.setCircle(36);
      rock.setData("hp", 24);
      rock.setData("maxHp", 24);
    }
  }

  emitShipState(time) {
    if (time - this.lastShipStateEmit < 50) {
      return;
    }

    this.lastShipStateEmit = time;
    this.hooks.onStateUpdate({
      x: this.player.x,
      y: this.player.y,
      rotation: this.player.rotation,
      velocityX: this.player.body.velocity.x,
      velocityY: this.player.body.velocity.y,
      health: this.playerHealth,
    });
  }

  syncRemoteShips() {
    const players = this.hooks.getRemotePlayers();
    const activeIds = new Set();

    players.forEach((player) => {
      if (!player.state || player.socketId === this.ownSocketId) {
        return;
      }

      activeIds.add(player.socketId);
      let ship = this.remoteShips.get(player.socketId);

      if (!ship) {
        const sprite = this.add.image(player.state.x, player.state.y, "ship-remote");
        sprite.setDepth(10);
        const label = this.add
          .text(player.state.x, player.state.y - 40, player.name, {
            font: "12px monospace",
            fill: "#f59e0b",
          })
          .setOrigin(0.5, 0.5)
          .setDepth(11);
        ship = { sprite, label };
        this.remoteShips.set(player.socketId, ship);
      }

      ship.sprite.x = Phaser.Math.Linear(ship.sprite.x, player.state.x, 0.35);
      ship.sprite.y = Phaser.Math.Linear(ship.sprite.y, player.state.y, 0.35);
      ship.sprite.rotation = player.state.rotation;
      ship.label.setPosition(ship.sprite.x, ship.sprite.y - 40);
      ship.label.setText(player.name);
    });

    [...this.remoteShips.entries()].forEach(([socketId, ship]) => {
      if (activeIds.has(socketId)) {
        return;
      }

      ship.sprite.destroy();
      ship.label.destroy();
      this.remoteShips.delete(socketId);
    });
  }

  fireProjectile(time) {
    const fireRate = this.weaponStats.fireRateMs;
    if (time - this.lastShotAt < fireRate) {
      return;
    }

    this.lastShotAt = time;

    const pointer = this.input.activePointer;
    const aimAngle = Phaser.Math.Angle.Between(
      this.player.x,
      this.player.y,
      pointer.worldX,
      pointer.worldY,
    );

    const bullet = this.bullets.get(this.player.x, this.player.y, "projectile");
    if (!bullet) {
      return;
    }

    bullet.enableBody(true, this.player.x, this.player.y, true, true);
    bullet.setDepth(9);
    bullet.body.setAllowGravity(false);
    bullet.setData("bornAt", time);
    bullet.setVelocity(
      Math.cos(aimAngle) * this.weaponStats.projectileSpeed,
      Math.sin(aimAngle) * this.weaponStats.projectileSpeed,
    );

    // #region agent log
    writeDebugLog({
      hypothesisId: "H1",
      location: "SpaceGame.jsx:fireProjectile",
      message: "Projectile fired",
      data: { bulletActive: bullet.active, fireRate: fireRate },
    });
    // #endregion

    this.applyAutoHit(aimAngle);
  }

  hitRock(bullet, rock) {
    // #region agent log
    writeDebugLog({
      hypothesisId: "H1",
      location: "SpaceGame.jsx:hitRock",
      message: "Bullet-rock overlap callback fired",
      data: { rockActive: Boolean(rock?.active), bulletActive: Boolean(bullet?.active) },
    });
    // #endregion

    bullet.disableBody(true, true);
    this.damageRock(rock);
  }

  damageRock(rock) {
    if (!rock?.active) {
      return;
    }

    const previousHp = rock.getData("hp") ?? 24;
    const hp = previousHp - this.weaponStats.projectileDamage;

    // #region agent log
    writeDebugLog({
      hypothesisId: "H3",
      location: "SpaceGame.jsx:damageRock",
      message: "Applying rock damage",
      data: {
        previousHp: previousHp,
        projectileDamage: this.weaponStats.projectileDamage,
        nextHp: hp,
      },
    });
    // #endregion

    rock.setData("hp", hp);

    if (hp > 0) {
      return;
    }

    const lootDrop = this.loot.create(rock.x, rock.y, "loot");
    lootDrop.setData("item", Phaser.Utils.Array.GetRandom(LOOT_ITEMS));
    lootDrop.setDepth(8);
    lootDrop.setCircle(8);

    // #region agent log
    writeDebugLog({
      hypothesisId: "H4",
      location: "SpaceGame.jsx:damageRock",
      message: "Rock destroyed and loot dropped",
      data: { lootActive: Boolean(lootDrop?.active), x: rock.x, y: rock.y },
    });
    // #endregion

    rock.destroy();
  }

  applyAutoHit(aimAngle) {
    const rockCandidates = this.rocks.getChildren().filter((rock) => rock.active);
    if (rockCandidates.length === 0) {
      return;
    }

    let bestRock = null;
    let bestScore = Number.POSITIVE_INFINITY;

    rockCandidates.forEach((rock) => {
      const distance = Phaser.Math.Distance.Between(
        this.player.x,
        this.player.y,
        rock.x,
        rock.y,
      );
      if (distance > 320) {
        return;
      }

      const rockAngle = Phaser.Math.Angle.Between(
        this.player.x,
        this.player.y,
        rock.x,
        rock.y,
      );
      const angleDiff = Math.abs(Phaser.Math.Angle.Wrap(rockAngle - aimAngle));
      if (angleDiff > 0.55) {
        return;
      }

      const score = angleDiff * 200 + distance;
      if (score < bestScore) {
        bestScore = score;
        bestRock = rock;
      }
    });

    if (bestRock) {
      this.damageRock(bestRock);
    }
  }

  collectLoot(playerSprite, lootSprite) {
    const itemName = lootSprite.getData("item");
    this.cargo[itemName] = (this.cargo[itemName] ?? 0) + 1;
    this.hooks.onCargoChange({ ...this.cargo });
    this.hooks.onProgressGain(8);
    lootSprite.destroy();
  }

  damageOnCollision() {
    const now = this.time.now;
    if (now - this.lastCollisionDamage < 350) {
      return;
    }

    this.lastCollisionDamage = now;
    this.playerHealth = Math.max(0, this.playerHealth - 4);
    this.hooks.onHealthChange(this.playerHealth);

    if (this.playerHealth === 0) {
      this.player.setPosition(PLAYER_SPAWN.x, PLAYER_SPAWN.y);
      this.player.setVelocity(0, 0);
      this.playerHealth = 100;
      this.hooks.onHealthChange(this.playerHealth);
    }
  }

  updateHud() {
    const roomStats = this.hooks.getRoomStats();
    this.hudText.setText(
      [
        `Hull: ${this.playerHealth}/100`,
        `Room: ${roomStats.roomCode || "-"}`,
        `Players: ${roomStats.playerCount}`,
        "Controls: WASD move, Mouse aim/fire, SPACE brake, TAB cargo, E station",
      ].join("\n"),
    );

    this.isNearStation = Phaser.Math.Distance.Between(
      this.player.x,
      this.player.y,
      this.station.x,
      this.station.y,
    ) < 240;

    this.promptText.setText(this.isNearStation ? "Press E to open station dialog" : "");
  }

  updateMinimap() {
    const mapSize = 170;
    const mapX = this.scale.width - mapSize - 16;
    const mapY = 16;
    const scale = mapSize / WORLD_SIZE;

    this.minimap.clear();
    this.minimap.fillStyle(0x0f172a, 0.8);
    this.minimap.fillRect(mapX, mapY, mapSize, mapSize);
    this.minimap.lineStyle(1, 0x64748b, 1);
    this.minimap.strokeRect(mapX, mapY, mapSize, mapSize);

    this.minimap.fillStyle(0x38bdf8, 1);
    this.minimap.fillCircle(mapX + this.station.x * scale, mapY + this.station.y * scale, 3);

    this.minimap.fillStyle(0x22d3ee, 1);
    this.minimap.fillCircle(mapX + this.player.x * scale, mapY + this.player.y * scale, 3);

    this.remoteShips.forEach((ship) => {
      this.minimap.fillStyle(0xf59e0b, 1);
      this.minimap.fillCircle(mapX + ship.sprite.x * scale, mapY + ship.sprite.y * scale, 3);
    });
  }

  update(time) {
    let accelX = 0;
    let accelY = 0;
    const accelStep = SHIPS["Nem-1"].acceleration;

    if (this.keys.W.isDown) {
      accelY -= accelStep;
    }
    if (this.keys.S.isDown) {
      accelY += accelStep;
    }
    if (this.keys.A.isDown) {
      accelX -= accelStep;
    }
    if (this.keys.D.isDown) {
      accelX += accelStep;
    }

    this.player.setAcceleration(accelX, accelY);
    this.player.setDrag(this.keys.SPACE.isDown ? 700 : 280);

    const pointer = this.input.activePointer;
    const facingAngle = Phaser.Math.Angle.Between(
      this.player.x,
      this.player.y,
      pointer.worldX,
      pointer.worldY,
    );
    this.player.rotation = facingAngle + Math.PI / 2;

    if (pointer.isDown) {
      this.fireProjectile(time);
    }

    this.bullets.children.each((bullet) => {
      if (!bullet.active) {
        return;
      }

      if (time - (bullet.getData("bornAt") ?? time) > 1000) {
        bullet.disableBody(true, true);
      }
    });

    if (this.isNearStation && Phaser.Input.Keyboard.JustDown(this.keys.E)) {
      this.hooks.onStationInteract();
    }

    this.syncRemoteShips();
    this.emitShipState(time);
    this.updateHud();
    this.updateMinimap();
  }
}

export function SpaceGame({
  ownSocketId,
  roomCode,
  players,
  onStateUpdate,
  onProgressGain,
  onCargoChange,
  onHealthChange,
  onToggleCargo,
  onStationInteract,
}) {
  const containerRef = useRef(null);
  const gameRef = useRef(null);

  const playersRef = useRef(players);
  const roomCodeRef = useRef(roomCode);
  const onStateUpdateRef = useRef(onStateUpdate);
  const onProgressGainRef = useRef(onProgressGain);
  const onCargoChangeRef = useRef(onCargoChange);
  const onHealthChangeRef = useRef(onHealthChange);
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
    onToggleCargoRef.current = onToggleCargo;
  }, [onToggleCargo]);

  useEffect(() => {
    onStationInteractRef.current = onStationInteract;
  }, [onStationInteract]);

  useEffect(() => {
    if (!containerRef.current || !ownSocketId) {
      return;
    }

    // #region agent log
    writeDebugLog({
      hypothesisId: "H2",
      location: "SpaceGame.jsx:useEffect",
      message: "SpaceGame effect init",
      data: { ownSocketId: ownSocketId, roomCode: roomCodeRef.current },
    });
    // #endregion

    const hooks = {
      getRemotePlayers: () => playersRef.current,
      getRoomStats: () => ({
        roomCode: roomCodeRef.current,
        playerCount: playersRef.current.length,
      }),
      onStateUpdate: (...args) => onStateUpdateRef.current?.(...args),
      onProgressGain: (...args) => onProgressGainRef.current?.(...args),
      onCargoChange: (...args) => onCargoChangeRef.current?.(...args),
      onHealthChange: (...args) => onHealthChangeRef.current?.(...args),
      onToggleCargo: (...args) => onToggleCargoRef.current?.(...args),
      onStationInteract: (...args) => onStationInteractRef.current?.(...args),
    };

    const scene = new SpacePortScene({ hooks, ownSocketId });
    const game = new Phaser.Game({
      type: Phaser.AUTO,
      parent: containerRef.current,
      width: 960,
      height: 620,
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
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH,
      },
      render: {
        antialias: true,
      },
    });

    gameRef.current = game;

    return () => {
      // #region agent log
      writeDebugLog({
        hypothesisId: "H2",
        location: "SpaceGame.jsx:useEffect",
        message: "SpaceGame effect cleanup",
        data: { ownSocketId: ownSocketId, roomCode: roomCodeRef.current },
      });
      // #endregion

      game.destroy(true);
      gameRef.current = null;
    };
  }, [
    ownSocketId,
  ]);

  return <div className="game-canvas" ref={containerRef} />;
}
