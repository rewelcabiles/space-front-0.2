export const normalizeRoomCode = (value) => value?.trim().toUpperCase() ?? "";

export const normalizePlayerName = (value) => value?.trim() ?? "";

const isFiniteNumber = (value) => Number.isFinite(value);

export const isValidProgress = (value) => {
  if (!value || typeof value !== "object") {
    return false;
  }

  const { level, experience } = value;
  return Number.isInteger(level) && level >= 1 &&
    Number.isInteger(experience) && experience >= 0;
};

export const isValidPlayerState = (value) => {
  if (!value || typeof value !== "object") {
    return false;
  }

  const { x, y, rotation, velocityX, velocityY, health } = value;
  return isFiniteNumber(x) &&
    isFiniteNumber(y) &&
    isFiniteNumber(rotation) &&
    isFiniteNumber(velocityX) &&
    isFiniteNumber(velocityY) &&
    isFiniteNumber(health);
};
