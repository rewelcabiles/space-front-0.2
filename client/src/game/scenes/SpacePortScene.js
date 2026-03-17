import Phaser from "phaser";

const WORLD_SIZE = 2400;
const PLAYER_SPAWN = { x: WORLD_SIZE / 2, y: WORLD_SIZE / 2 };

const toSpritePath = (fileName, fallbackName) => {
  const baseName = (fileName || fallbackName || "").replace(".png", ".svg");
  return `/sprites/${baseName}`;
};

export class SpacePortScene extends Phaser.Scene {
  constructor({ hooks, content }) {
    super({ key: "space-port" });
    this.hooks = hooks;
    this.content = content;
    this.remoteShips = new Map();
    this.lastShipStateEmit = 0;
    this.lastCollisionDamage = 0;
    this.isNearStation = false;
  }

  preload() {
    this.load.image(
      "ship-local",
      toSpritePath(this.content.ship.image, "nem-1.svg"),
    );
    this.load.image(
      "ship-remote",
      toSpritePath(this.content.ship.image, "nem-1.svg"),
    );
    this.load.image("rock", "/sprites/asteroid_1.svg");
    this.load.image("loot", "/sprites/rock_drop_1.svg");
    this.load.image("station", "/sprites/space_station_1.svg");
  }

  create() {
    this.cameras.main.setBackgroundColor("#020617");
    this.physics.world.setBounds(0, 0, WORLD_SIZE, WORLD_SIZE);
    this.drawBackgroundStars();

    this.player = this.physics.add.image(PLAYER_SPAWN.x, PLAYER_SPAWN.y, "ship-local");
    this.player.setCollideWorldBounds(true);
    this.player.setDrag(360, 360);
    this.player.setMaxVelocity(this.content.ship.max_speed * 2);
    this.player.setScale(0.9);
    this.playerHealth = 100;
    this.cargo = {};

    this.bullets = this.physics.add.group({
      classType: Phaser.Physics.Arcade.Image,
      maxSize: 120,
    });
    this.lastShotAt = 0;

    this.rocks = this.physics.add.group({ immovable: true, allowGravity: false });
    this.spawnRocks(16);

    this.loot = this.physics.add.group({ allowGravity: false, immovable: true });
    this.station = this.physics.add.image(
      PLAYER_SPAWN.x - 120,
      PLAYER_SPAWN.y - 120,
      "station",
    );
    this.station.setScale(0.55);
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

    this.keys = this.input.keyboard.addKeys("W,A,S,D,SPACE,TAB,E,F");
    this.input.keyboard.on("keydown-E", () => {
      if (this.isNearStation) {
        this.hooks.onStationInteract();
      }
    });
    this.input.keyboard.on("keydown-TAB", (event) => {
      event.preventDefault();
      this.hooks.onToggleCargo();
    });
    this.input.on("pointerdown", () => {
      this.fireProjectile(this.time.now);
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
  }

  drawBackgroundStars() {
    const stars = this.add.graphics();
    stars.fillStyle(0xffffff, 0.55);
    for (let i = 0; i < 260; i += 1) {
      stars.fillCircle(
        Phaser.Math.Between(0, WORLD_SIZE),
        Phaser.Math.Between(0, WORLD_SIZE),
        Phaser.Math.Between(1, 2),
      );
    }
  }

  spawnRocks(count) {
    const starterRock = this.rocks.create(
      PLAYER_SPAWN.x + 120,
      PLAYER_SPAWN.y - 20,
      "rock",
    );
    starterRock.setCircle(34);
    starterRock.setScale(0.75);
    starterRock.setData("hp", 8);

    for (let i = 0; i < count; i += 1) {
      const rock = this.rocks.create(
        Phaser.Math.Between(140, WORLD_SIZE - 140),
        Phaser.Math.Between(140, WORLD_SIZE - 140),
        "rock",
      );
      rock.setCircle(34);
      rock.setScale(0.75);
      rock.setData("hp", 12);
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
      if (!player.state || player.socketId === this.hooks.getOwnSocketId()) {
        return;
      }

      activeIds.add(player.socketId);
      let ship = this.remoteShips.get(player.socketId);
      if (!ship) {
        const sprite = this.add.image(player.state.x, player.state.y, "ship-remote");
        sprite.setScale(0.9);
        sprite.setTint(0xf59e0b);
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
    const fireRateMs = Math.max(
      80,
      Math.round((this.content.module.type_data?.fire_rate ?? 0.4) * 1000),
    );
    if (time - this.lastShotAt < fireRateMs) {
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
    const bullet = this.bullets.get(this.player.x, this.player.y, "loot");
    if (!bullet) {
      return;
    }

    bullet.enableBody(true, this.player.x, this.player.y, true, true);
    bullet.setScale(0.7);
    bullet.setTint(0xe2e8f0);
    bullet.setDepth(9);
    bullet.body.setAllowGravity(false);
    bullet.setData("bornAt", time);

    const speed = this.content.module.type_data?.proj_speed ?? 400;
    bullet.setVelocity(Math.cos(aimAngle) * speed, Math.sin(aimAngle) * speed);

    this.applyAutoHit(aimAngle);
  }

  applyAutoHit(aimAngle) {
    const candidates = this.rocks.getChildren().filter((rock) => rock.active);
    let bestRock = null;
    let bestScore = Number.POSITIVE_INFINITY;

    candidates.forEach((rock) => {
      const distance = Phaser.Math.Distance.Between(
        this.player.x,
        this.player.y,
        rock.x,
        rock.y,
      );
      if (distance > 620) {
        return;
      }
      const rockAngle = Phaser.Math.Angle.Between(
        this.player.x,
        this.player.y,
        rock.x,
        rock.y,
      );
      const angleDiff = Math.abs(Phaser.Math.Angle.Wrap(rockAngle - aimAngle));
      const score = angleDiff * 40 + distance;
      if (score < bestScore) {
        bestScore = score;
        bestRock = rock;
      }
    });

    if (bestRock) {
      this.damageRock(bestRock);
    }
  }

  hitRock(bullet, rock) {
    bullet.disableBody(true, true);
    this.damageRock(rock);
  }

  damageRock(rock) {
    if (!rock?.active) {
      return;
    }
    const damage = this.content.module.type_data?.proj_damage ?? 4;
    const hp = (rock.getData("hp") ?? 12) - damage;
    rock.setData("hp", hp);
    if (hp > 0) {
      return;
    }

    const lootDrop = this.loot.create(rock.x, rock.y, "loot");
    lootDrop.setScale(0.8);
    lootDrop.setData("item", Phaser.Utils.Array.GetRandom(this.content.lootItemNames));
    lootDrop.setDepth(8);
    lootDrop.setCircle(10);
    // Keeps pickup responsive in cloud testing while preserving cargo loop.
    this.collectLoot(this.player, lootDrop);
    rock.destroy();
  }

  collectLoot(_player, lootSprite) {
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
        "Controls: WASD move, Mouse/F fire, SPACE brake, TAB cargo, E station",
      ].join("\n"),
    );

    this.isNearStation = Phaser.Math.Distance.Between(
      this.player.x,
      this.player.y,
      this.station.x,
      this.station.y,
    ) < 220;
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
    const acceleration = (this.content.ship.acceleration ?? 1.5) * 420;

    if (this.keys.W.isDown) {
      accelY -= acceleration;
    }
    if (this.keys.S.isDown) {
      accelY += acceleration;
    }
    if (this.keys.A.isDown) {
      accelX -= acceleration;
    }
    if (this.keys.D.isDown) {
      accelX += acceleration;
    }

    this.player.setAcceleration(accelX, accelY);
    this.player.setDrag(this.keys.SPACE.isDown ? 800 : 360);

    const pointer = this.input.activePointer;
    const facingAngle = Phaser.Math.Angle.Between(
      this.player.x,
      this.player.y,
      pointer.worldX,
      pointer.worldY,
    );
    this.player.rotation = facingAngle + Math.PI / 2;

    if (pointer.isDown || this.keys.F.isDown) {
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
