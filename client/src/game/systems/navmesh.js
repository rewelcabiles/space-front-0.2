const buildKey = (x, y) => `${x},${y}`;

const worldToCell = (value, cellSize) => Math.floor(value / cellSize);
const cellToWorld = (cell, cellSize) => cell * cellSize + cellSize * 0.5;

const heuristic = (a, b) => Math.abs(a.x - b.x) + Math.abs(a.y - b.y);

const parseKey = (key) => {
  const [x, y] = key.split(",").map((value) => Number(value));
  return { x, y };
};

const neighbors = [
  { x: 1, y: 0, cost: 1 },
  { x: -1, y: 0, cost: 1 },
  { x: 0, y: 1, cost: 1 },
  { x: 0, y: -1, cost: 1 },
  { x: 1, y: 1, cost: 1.4 },
  { x: 1, y: -1, cost: 1.4 },
  { x: -1, y: 1, cost: 1.4 },
  { x: -1, y: -1, cost: 1.4 },
];

export const buildNavMesh = ({
  worldSize,
  cellSize,
  circularObstacles,
}) => {
  const cellsPerAxis = Math.ceil(worldSize / cellSize);
  const blocked = new Set();

  circularObstacles.forEach((obstacle) => {
    const minX = Math.max(0, worldToCell(obstacle.x - obstacle.radius, cellSize));
    const maxX = Math.min(cellsPerAxis - 1, worldToCell(obstacle.x + obstacle.radius, cellSize));
    const minY = Math.max(0, worldToCell(obstacle.y - obstacle.radius, cellSize));
    const maxY = Math.min(cellsPerAxis - 1, worldToCell(obstacle.y + obstacle.radius, cellSize));

    for (let cellX = minX; cellX <= maxX; cellX += 1) {
      for (let cellY = minY; cellY <= maxY; cellY += 1) {
        const centerX = cellToWorld(cellX, cellSize);
        const centerY = cellToWorld(cellY, cellSize);
        const dx = centerX - obstacle.x;
        const dy = centerY - obstacle.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        if (distance <= obstacle.radius + cellSize * 0.3) {
          blocked.add(buildKey(cellX, cellY));
        }
      }
    }
  });

  const findPath = (startWorld, targetWorld) => {
    const start = {
      x: worldToCell(startWorld.x, cellSize),
      y: worldToCell(startWorld.y, cellSize),
    };
    const goal = {
      x: worldToCell(targetWorld.x, cellSize),
      y: worldToCell(targetWorld.y, cellSize),
    };

    const inBounds = (point) =>
      point.x >= 0 && point.y >= 0 && point.x < cellsPerAxis && point.y < cellsPerAxis;
    if (!inBounds(start) || !inBounds(goal)) {
      return [];
    }

    const startKey = buildKey(start.x, start.y);
    const goalKey = buildKey(goal.x, goal.y);
    if (blocked.has(startKey) || blocked.has(goalKey)) {
      return [];
    }

    const open = [{ ...start, key: startKey }];
    const openSet = new Set([startKey]);
    const gScore = new Map([[startKey, 0]]);
    const fScore = new Map([[startKey, heuristic(start, goal)]]);
    const cameFrom = new Map();

    while (open.length > 0) {
      open.sort((a, b) => (fScore.get(a.key) ?? Infinity) - (fScore.get(b.key) ?? Infinity));
      const current = open.shift();
      openSet.delete(current.key);

      if (current.key === goalKey) {
        const pathCells = [current.key];
        while (cameFrom.has(pathCells[0])) {
          pathCells.unshift(cameFrom.get(pathCells[0]));
        }
        return pathCells.map((cellKey) => {
          const point = parseKey(cellKey);
          return {
            x: cellToWorld(point.x, cellSize),
            y: cellToWorld(point.y, cellSize),
          };
        });
      }

      neighbors.forEach((direction) => {
        const neighbor = {
          x: current.x + direction.x,
          y: current.y + direction.y,
        };
        if (!inBounds(neighbor)) {
          return;
        }

        const neighborKey = buildKey(neighbor.x, neighbor.y);
        if (blocked.has(neighborKey)) {
          return;
        }

        const tentativeScore = (gScore.get(current.key) ?? Infinity) + direction.cost;
        if (tentativeScore >= (gScore.get(neighborKey) ?? Infinity)) {
          return;
        }

        cameFrom.set(neighborKey, current.key);
        gScore.set(neighborKey, tentativeScore);
        fScore.set(neighborKey, tentativeScore + heuristic(neighbor, goal));

        if (!openSet.has(neighborKey)) {
          open.push({ ...neighbor, key: neighborKey });
          openSet.add(neighborKey);
        }
      });
    }

    return [];
  };

  return {
    cellSize,
    blocked,
    cellsPerAxis,
    findPath,
  };
};
