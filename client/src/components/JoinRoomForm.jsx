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
        Player name
        <input
          value={playerName}
          onChange={(event) => onChangePlayerName(event.target.value)}
          placeholder="ex: NovaPilot"
        />
      </label>

      <label>
        Room code
        <input
          value={roomCode}
          onChange={(event) => onChangeRoomCode(event.target.value)}
          placeholder="ex: ALFA"
        />
      </label>

      <button type="submit">Join room</button>
    </form>
  );
}
