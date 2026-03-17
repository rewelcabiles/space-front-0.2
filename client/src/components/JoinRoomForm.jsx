export function JoinRoomForm({
  playerName,
  roomCode,
  onChangePlayerName,
  onChangeRoomCode,
  onSubmit,
}) {
  return (
    <form className="join-form" onSubmit={onSubmit}>
      <label>
        Callsign
        <input
          value={playerName}
          onChange={(event) => onChangePlayerName(event.target.value)}
          placeholder="ex: NovaPilot"
        />
      </label>

      <label>
        Sector code
        <input
          value={roomCode}
          onChange={(event) => onChangeRoomCode(event.target.value)}
          placeholder="ex: ALFA"
        />
      </label>

      <button type="submit">Enter sector</button>
    </form>
  );
}
