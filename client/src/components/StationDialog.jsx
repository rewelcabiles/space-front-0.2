import { useEffect, useMemo, useState } from "react";

import { buildDialogueOptions, getDialogueNode, resolveSetNode } from "../game/dialogue";

export function StationDialog({
  dialogueMap,
  nodeId,
  onSelectNode,
  moduleCatalog,
  itemCatalog,
  progress,
  onClose,
}) {
  const [section, setSection] = useState("dock");

  useEffect(() => {
    setSection("dock");
  }, [nodeId]);

  const rawNode = useMemo(
    () => getDialogueNode(dialogueMap, nodeId),
    [dialogueMap, nodeId],
  );
  const node = useMemo(
    () => resolveSetNode(dialogueMap, rawNode),
    [dialogueMap, rawNode],
  );

  if (!node) {
    return null;
  }

  const options = buildDialogueOptions(dialogueMap, node);
  const body = node.name || node.title || "";
  const moduleEntries = Object.entries(moduleCatalog ?? {});
  const itemEntries = Object.entries(itemCatalog ?? {});

  const openDialogueNext = (next) => {
    if (!next) {
      return;
    }
    onSelectNode(next);
    setSection("hangar");
  };

  return (
    <section className="dialog-overlay">
      <div className="dialog-card">
        <div className="station-tabs">
          <button type="button" className={section === "dock" ? "active-tab" : ""} onClick={() => setSection("dock")}>Dock</button>
          <button type="button" className={section === "hangar" ? "active-tab" : ""} onClick={() => setSection("hangar")}>Hangar</button>
          <button type="button" className={section === "mechanic" ? "active-tab" : ""} onClick={() => setSection("mechanic")}>Mechanic</button>
          <button type="button" className={section === "jobs" ? "active-tab" : ""} onClick={() => setSection("jobs")}>Job Board</button>
          <button type="button" className="ghost" onClick={onClose}>Close</button>
        </div>

        {section === "dock" && (
          <>
            <p className="dialog-actor">Station Services</p>
            <h3>Docking bay</h3>
            <p>Select a station service to continue.</p>
            <div className="dialog-options">
              <button type="button" onClick={() => setSection("hangar")}>Enter hangar dialogue</button>
              <button type="button" onClick={() => setSection("mechanic")}>Visit mechanic</button>
              <button type="button" onClick={() => setSection("jobs")}>Open job board</button>
            </div>
          </>
        )}

        {section === "hangar" && (
          <>
            {node.actor && <p className="dialog-actor">{node.actor}</p>}
            <h3>{node.title || "Hangar dialogue"}</h3>
            <p>{body}</p>
            <div className="dialog-options">
              {options.map((option, index) => (
                <button
                  key={`${option.label}-${index}`}
                  type="button"
                  onClick={() => openDialogueNext(option.next)}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </>
        )}

        {section === "mechanic" && (
          <>
            <p className="dialog-actor">Mechanic Bay</p>
            <h3>Module diagnostics</h3>
            <ul className="cargo-list">
              {moduleEntries.map(([moduleName, definition]) => (
                <li key={moduleName}>
                  <span>{moduleName}</span>
                  <span>
                    {definition.module_space_requirement ?? 0} slot(s)
                  </span>
                </li>
              ))}
            </ul>
          </>
        )}

        {section === "jobs" && (
          <>
            <p className="dialog-actor">Job Board</p>
            <h3>Active contracts</h3>
            <ul className="cargo-list">
              <li>
                <span>Mine local debris field</span>
                <span>{progress.experience}/100 XP</span>
              </li>
              <li>
                <span>Collect resources</span>
                <span>{itemEntries.length} known item classes</span>
              </li>
            </ul>
          </>
        )}
      </div>
    </section>
  );
}
