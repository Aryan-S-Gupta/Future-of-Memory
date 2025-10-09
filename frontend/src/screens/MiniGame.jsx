import { useState, useEffect } from "react";
import api from "../../api/multiplayer/api.js"; // axios instance
import Button from "../components/Button/Button.jsx";

const EMOJIS = ["🍎","🍌","🍇","🍒","🍉","🥝","🍍","🍓"];
const DISPLAY_TIME = 5000;
const GRID_SIZE = 6;

const MemoryMiniGame = ({ roomCode, turnId, tiedPlayers, optionMap, playerName, onFinish }) => {
  const [sequence, setSequence] = useState([]);
  const [hidden, setHidden] = useState(false);
  const [userSelection, setUserSelection] = useState([]);
  const [score, setScore] = useState(0);
  const [submitted, setSubmitted] = useState(false);
  const [pollingData, setPollingData] = useState(null);

  useEffect(() => {
    const shuffled = EMOJIS.sort(() => 0.5 - Math.random()).slice(0, GRID_SIZE);
    setSequence(shuffled);
    const timer = setTimeout(() => setHidden(true), DISPLAY_TIME);
    return () => clearTimeout(timer);
  }, []);

  const handleClick = (emoji) => {
    if (hidden && !submitted) {
      setUserSelection((prev) => [...prev, emoji]);
    }
  };

  const handleSubmit = async () => {
    if (submitted) return;

    let points = userSelection.reduce(
      (acc, val, idx) => acc + (sequence[idx] === val ? 10 : 0),
      0
    );
    points += Math.max(0, GRID_SIZE * 2 - userSelection.length);
    setScore(points);
    setSubmitted(true);

    try {
      await api.post("/minigame/submit-score", {
        room_code: roomCode,
        turn_id: turnId,
        player_name: playerName,
        score: points
      });
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (!submitted) return;

    const interval = setInterval(async () => {
      try {
        const res = await api.get(`/minigame/status/${roomCode}/${turnId}`);
        setPollingData(res.data);
        if (res.data.status === "resolved") {
          clearInterval(interval);
          onFinish(res.data.winning_option, res.data.winner);
        }
      } catch (err) {
        console.error(err);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [submitted]);

  return (
    <div className="memory-minigame">
      <h2>Memory Mini-Game</h2>
      <div className="emoji-grid">
        {sequence.map((emoji, idx) => (
          <div
            key={idx}
            className={`card ${hidden ? "flipped" : ""} ${submitted ? "disabled" : ""}`}
            onClick={() => handleClick(emoji)}
          >
            <div className="card-inner">
              <div className="card-front">❓</div>
              <div className="card-back">{emoji}</div>
            </div>
          </div>
        ))}
      </div>

      {!submitted && hidden && (
        <Button title="Submit" baseButton="btn-primary" action={handleSubmit} />
      )}

      {submitted && (
        <div>
          <p>Your score: {score}</p>
          <p>Waiting for other players...</p>
        </div>
      )}

      {pollingData && pollingData.status === "resolved" && (
        <div>
          <p>Winner: {pollingData.winner}</p>
          <p>Winning Option: {pollingData.winning_option}</p>
        </div>
      )}
    </div>
  );
};

export default MemoryMiniGame;
