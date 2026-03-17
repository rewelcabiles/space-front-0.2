import Phaser from "phaser";

export const createAiPilot = (scene, {
  textureKey,
  startX,
  startY,
  maxSpeed,
}) => {
  const sprite = scene.physics.add.image(startX, startY, textureKey);
  sprite.setScale(0.88);
  sprite.setTint(0xa78bfa);
  sprite.setDrag(320, 320);
  sprite.setMaxVelocity(maxSpeed);
  sprite.setDepth(9);

  const label = scene.add
    .text(startX, startY - 34, "Buzz", {
      font: "12px monospace",
      color: "#c4b5fd",
    })
    .setOrigin(0.5, 0.5)
    .setDepth(11);

  let path = [];
  let pathIndex = 0;
  let nextRepathAt = 0;
  let isPathing = false;

  const repath = (time, navMesh, target) => {
    path = navMesh.findPath({ x: sprite.x, y: sprite.y }, target);
    pathIndex = 0;
    nextRepathAt = time + 1200;
    isPathing = path.length > 1;
  };

  const update = (time, _delta, { navMesh, target, forceRepath = false }) => {
    if (!navMesh) {
      return;
    }

    if (forceRepath || time >= nextRepathAt || path.length === 0) {
      repath(time, navMesh, target);
    }

    if (!isPathing) {
      sprite.setAcceleration(0, 0);
      sprite.setVelocity(
        Phaser.Math.Linear(sprite.body.velocity.x, 0, 0.08),
        Phaser.Math.Linear(sprite.body.velocity.y, 0, 0.08),
      );
      label.setPosition(sprite.x, sprite.y - 34);
      return;
    }

    const targetPoint = path[Math.min(pathIndex + 1, path.length - 1)];
    const distance = Phaser.Math.Distance.Between(sprite.x, sprite.y, targetPoint.x, targetPoint.y);
    if (distance < 24 && pathIndex < path.length - 1) {
      pathIndex += 1;
    }

    const angle = Phaser.Math.Angle.Between(sprite.x, sprite.y, targetPoint.x, targetPoint.y);
    const acceleration = 460;
    sprite.setAcceleration(Math.cos(angle) * acceleration, Math.sin(angle) * acceleration);
    sprite.rotation = angle + Math.PI / 2;
    label.setPosition(sprite.x, sprite.y - 34);
  };

  return {
    sprite,
    label,
    update,
    getPathLength: () => path.length,
    isPathing: () => isPathing,
    destroy: () => {
      sprite.destroy();
      label.destroy();
    },
  };
};
