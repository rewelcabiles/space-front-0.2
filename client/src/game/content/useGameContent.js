import { useEffect, useMemo, useState } from "react";

import { fallbackGameContent } from "./fallbackGameContent";

export const useGameContent = (serverUrl) => {
  const [content, setContent] = useState(fallbackGameContent);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const response = await fetch(`${serverUrl}/api/game-content`);
        if (!response.ok) {
          return;
        }
        const payload = await response.json();
        if (!cancelled) {
          setContent(payload);
        }
      } catch {
        // Use fallback content when endpoint is unavailable.
      }
    };

    load();
    return () => {
      cancelled = true;
    };
  }, [serverUrl]);

  return useMemo(() => {
    const ship = content.ships["Nem-1"] ?? fallbackGameContent.ships["Nem-1"];
    const moduleCatalog = content.modules ?? fallbackGameContent.modules;
    const primaryModuleName = moduleCatalog["Projectile Cannon Mk1"]
      ? "Projectile Cannon Mk1"
      : Object.keys(moduleCatalog)[0];
    const module = moduleCatalog[primaryModuleName] ??
      fallbackGameContent.modules["Projectile Cannon Mk1"];
    const itemCatalog = content.items ?? fallbackGameContent.items;
    const stationRootId = "1950d26c-5cb6-414c-84d3-6fda48f842d4";
    const introRootId = "82ca9c3c-2a8f-4e80-a4d6-09d1958be31d";

    return {
      raw: content,
      ship,
      module,
      moduleCatalog,
      primaryModuleName,
      itemCatalog,
      lootItemNames: Object.keys(itemCatalog),
      stationDialogue: content.stationDialogue ?? fallbackGameContent.stationDialogue,
      introDialogue: content.dialogue ?? fallbackGameContent.dialogue,
      stationRootId,
      introRootId,
    };
  }, [content]);
};
