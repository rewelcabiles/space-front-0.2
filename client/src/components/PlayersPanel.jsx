export function PlayersPanel({ players }) {
  return (
    <section className="panel">
      <h3>Players in room</h3>
      <ul className="players">
        {players.map((player) => (
          <li key={player.socketId}>
            <span>{player.name}</span>
            <span>
              L{player.progress.level} - {player.progress.experience} XP
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
