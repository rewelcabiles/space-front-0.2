export function ModulePanel({
  installedModules,
  moduleSpaceUsed,
  maxModuleSpace,
  aiPathing,
  aiPathNodes,
}) {
  return (
    <section className="panel">
      <h3>Ship systems</h3>
      <p className="meta-line">
        Module space: {moduleSpaceUsed}/{maxModuleSpace}
      </p>
      <p className="meta-line">
        AI status: {aiPathing ? `Pathing (${aiPathNodes} nodes)` : "Idle"}
      </p>
      <ul className="cargo-list">
        {installedModules.map((moduleName) => (
          <li key={moduleName}>
            <span>{moduleName}</span>
            <span>Online</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
