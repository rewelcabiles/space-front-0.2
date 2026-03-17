export const fallbackGameContent = {
  ships: {
    "Nem-1": {
      class: "frigate",
      max_speed: 160,
      acceleration: 1.5,
      turn_speed: 8,
      moment: 40,
      mass: 5,
      color: [255, 55, 0],
      image: "nem-1.png",
      points: [
        [0, 0],
        [50, 25],
        [0, 50],
        [15, 25],
      ],
    },
  },
  modules: {
    "Projectile Cannon Mk1": {
      passive: false,
      module_space_requirement: 4,
      modifies: {
        max_hp: 5,
      },
      type: "projectile_weapon",
      type_data: {
        can_fire: false,
        fire_rate: 0.4,
        fire_rate_cd: 0,
        proj_damage: 4,
        proj_speed: 400,
      },
    },
  },
  items: {
    Rocks: {
      weight: 5,
      stackable: true,
      worth: 2,
      category: "resource",
      color: [0, 255, 0],
      image: "rock_drop_1.png",
      meta: { type: "rocks" },
    },
    Ochre: {
      weight: 1,
      stackable: true,
      worth: 4,
      type: "resource",
      color: [255, 255, 0],
      image: "rock_drop_1.png",
      meta: { type: "Jewels" },
    },
  },
  dialogue: {
    "82ca9c3c-2a8f-4e80-a4d6-09d1958be31d": {
      type: "Text",
      id: "82ca9c3c-2a8f-4e80-a4d6-09d1958be31d",
      actor: "Buzz",
      name: "We're here to mine some space rocks buddy, get to it!\n\n",
      next: null,
    },
  },
  stationDialogue: {
    "1950d26c-5cb6-414c-84d3-6fda48f842d4": {
      type: "Text",
      id: "1950d26c-5cb6-414c-84d3-6fda48f842d4",
      actor: "Narrator",
      name: "You step foot on the Hangar.\n",
      choices: ["e08e7704-8445-4972-b802-5da6c95d1c42"],
    },
    "e08e7704-8445-4972-b802-5da6c95d1c42": {
      type: "Choice",
      id: "e08e7704-8445-4972-b802-5da6c95d1c42",
      name: "",
      title: "Visit Bobs Ship Parts",
      next: "3b3c3f68-1019-46b5-addc-161fb035818c",
    },
    "3b3c3f68-1019-46b5-addc-161fb035818c": {
      type: "Text",
      id: "3b3c3f68-1019-46b5-addc-161fb035818c",
      actor: "Narrator",
      name: "The bell rings as you push open the door. You see Bob standing behind the counter.",
      choices: [
        "1d63b40d-de29-49b2-9b41-579d49c2c366",
        "c7fbcea8-c176-44f1-8c61-cafae68681e1",
      ],
    },
    "1d63b40d-de29-49b2-9b41-579d49c2c366": {
      type: "Choice",
      id: "1d63b40d-de29-49b2-9b41-579d49c2c366",
      name: "",
      title: "Head back to the hangar",
      next: "1950d26c-5cb6-414c-84d3-6fda48f842d4",
    },
    "c7fbcea8-c176-44f1-8c61-cafae68681e1": {
      type: "Choice",
      id: "c7fbcea8-c176-44f1-8c61-cafae68681e1",
      name: "",
      title: "Lemme see you got",
      next: "4fb21851-1fab-4725-8a21-b43268e66b44",
    },
    "4fb21851-1fab-4725-8a21-b43268e66b44": {
      type: "Set",
      id: "4fb21851-1fab-4725-8a21-b43268e66b44",
      variable: "view_shop",
      value: "bobs_wares",
      next: "1950d26c-5cb6-414c-84d3-6fda48f842d4",
    },
  },
};
