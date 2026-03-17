const normalizeType = (type) => String(type ?? "").toLowerCase();

export const getDialogueNode = (dialogueMap, nodeId) => dialogueMap?.[nodeId] ?? null;

export const resolveSetNode = (dialogueMap, node) => {
  if (!node) {
    return null;
  }
  if (normalizeType(node.type) !== "set") {
    return node;
  }
  return getDialogueNode(dialogueMap, node.next);
};

export const buildDialogueOptions = (dialogueMap, node) => {
  if (!node) {
    return [];
  }

  const type = normalizeType(node.type);
  if (type === "choice") {
    return [
      {
        label: node.title || "Continue",
        next: node.next ?? null,
      },
    ];
  }

  if (Array.isArray(node.choices)) {
    return node.choices
      .map((choiceId) => getDialogueNode(dialogueMap, choiceId))
      .filter(Boolean)
      .map((choiceNode) => ({
        label: choiceNode.title || choiceNode.name || "Continue",
        next: choiceNode.next ?? null,
      }));
  }

  if (node.next) {
    return [{ label: "Continue", next: node.next }];
  }

  return [{ label: "Close", next: null }];
};
