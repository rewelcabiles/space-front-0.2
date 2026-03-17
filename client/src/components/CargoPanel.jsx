export function CargoPanel({ cargo }) {
  return (
    <section className="panel">
      <h3>Cargo</h3>
      <ul className="cargo-list">
        {Object.keys(cargo).length === 0 && <li>Empty hold</li>}
        {Object.entries(cargo).map(([item, amount]) => (
          <li key={item}>
            <span>{item}</span>
            <span>x{amount}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
