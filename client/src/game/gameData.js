export const SHIPS = {
  "Nem-1": {
    maxSpeed: 300,
    acceleration: 600,
    turnSpeed: 12,
    color: 0x64b5f6,
  },
};

export const MODULES = {
  "Projectile Cannon Mk1": {
    fireRateMs: 200,
    projectileDamage: 12,
    projectileSpeed: 650,
  },
};

export const LOOT_ITEMS = ["Rocks", "Ochre"];

export const STATION_DIALOG = {
  "intro-1": {
    type: "text",
    actor: "Captain Indigo",
    title: "Welcome to Space Station 1",
    body: "We're here to mine some space rocks and keep this lane clear.",
    next: "choice-1",
  },
  "choice-1": {
    type: "choice",
    title: "What do you need?",
    options: [
      { text: "How can I help?", next: "help-1" },
      { text: "Maybe later.", next: "exit" },
    ],
  },
  "help-1": {
    type: "text",
    actor: "Captain Indigo",
    title: "Mining Brief",
    body: "Destroy rocks, collect ore, and level your ship with each haul.",
    next: "choice-1",
  },
};
