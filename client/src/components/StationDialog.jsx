import { buildDialogueOptions, getDialogueNode, resolveSetNode } from "../game/dialogue";

export function StationDialog({
  dialogueMap,
  nodeId,
  onSelectNode,
}) {
  const rawNode = getDialogueNode(dialogueMap, nodeId);
  const node = resolveSetNode(dialogueMap, rawNode);

  if (!node) {
    return null;
  }

  const options = buildDialogueOptions(dialogueMap, node);
  const body = node.name || node.title || "";

  return (
    <section className="dialog-overlay">
      <div className="dialog-card">
        {node.actor && <p className="dialog-actor">{node.actor}</p>}
        <h3>{node.title || "Station Dialogue"}</h3>
        <p>{body}</p>

        <div className="dialog-options">
          {options.map((option, index) => (
            <button
              key={`${option.label}-${index}`}
              type="button"
              onClick={() => onSelectNode(option.next)}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
