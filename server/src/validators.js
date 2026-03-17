export const normalizeRoomCode = (value) => value?.trim().toUpperCase() ?? "";

export const normalizePlayerName = (value) => value?.trim() ?? "";

export const isValidProgress = (value) => {
  if (!value || typeof value !== "object") {
    return false;
  }

  const { level, experience } = value;
  return Number.isInteger(level) && level >= 1 &&
    Number.isInteger(experience) && experience >= 0;
};
