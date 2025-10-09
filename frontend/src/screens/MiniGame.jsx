import { useState, useEffect, useRef } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import Button from "../components/Button/Button.jsx";
import api from "../../api/multiplayer/api.js"; // axios instance

const EMOJIS = ["🍎","🍌","🍇","🍒","🍉","🥝","🍍","🍓"]; // pool to pick from
const DISPLAY_TIME = 5000; // show emojis 5 seconds
const GRID_SIZE = 6; // 3x2 grid

const MemoryMiniGame = ({ roomCode, turnId, tiedPlayers, optionMap, playerName, onFinish }) => {
  const navigate = useNavigate();
  const [sequence, setSequence] = useState([]);
  const [hidden, setHidden] = useState(false);
  const [userSelection, setUserSelection] = useState([]);
  const [score, setScore] = useState(0);
  const [submitted, setSubmitted] = useState(false);
  const [pollingData, setPollingData] = useState(null);

  // Generate random sequence
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

    // Simple scoring: correct positions
    let points = userSelection.reduce(
      (acc, val, idx) => acc + (sequence[idx] === val ? 10 : 0),
      0
    );
    // Bonus for speed: faster = more points
    points += Math.max(0, GRID_SIZE * 2 - userSelection.length);

    setScore(points);
    setSubmitted(true);

    // Submit score to backend
    try {
      await api.post("/minigame/submit-score", {
        room_code: roomCode,
        turn_id: turnId,
        player_name: playerName,
        score: points
      });
    } catch (err) {
      console.error("Error submitting mini-game score:", err);
    }
  };

  // Poll backend to check if winner is determined
  useEffect(() => {
    if (!submitted) return;

    const interval = setInterval(async () => {
      try {
        const res = await api.get(`/minigame/status/${roomCode}/${turnId}`);
        setPollingData(res.data);

        if (res.data.status === "resolved") {
          clearInterval(interval);
          const winningOption = res.data.winning_option;
          onFinish(winningOption, res.data.winner); // continue main game
        }
      } catch (err) {
        console.error("Polling mini-game status failed:", err);
      }
    }, 3000); // every 3s

    return () => clearInterval(interval);
  }, [submitted]);

  return (
    <div className="memory-minigame">
      <h2>Memory Mini-Game</h2>
      {!hidden && <p>Memorize the sequence!</p>}
      <div className="emoji-grid" style={{ display: "grid", gridTemplateColumns: "repeat(3, 60px)", gap: "10px" }}>
        {(hidden ? EMOJIS : sequence).map((emoji, idx) => (
          <button
            key={idx}
            style={{
              width: "60px",
              height: "60px",
              fontSize: "2rem",
              cursor: hidden ? "pointer" : "default",
              opacity: hidden ? 1 : 0.5
            }}
            onClick={() => handleClick(emoji)}
            disabled={!hidden || submitted}
          >
            {hidden ? emoji : emoji}
          </button>
        ))}
      </div>

      {hidden && !submitted && (
        <div style={{ marginTop: "20px" }}>
          <p>Click the emojis in the original order!</p>
          <Button title="Submit" baseButton="btn-primary" action={handleSubmit} />
        </div>
      )}

      {submitted && (
        <div style={{ marginTop: "20px" }}>
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
