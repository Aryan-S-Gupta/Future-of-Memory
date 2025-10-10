import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "../styles/MemoryMiniGame.css";
import Button from "../components/Button/Button.jsx";

// 8 unique emojis for 4x4 grid (16 cards total)
const cardSymbols = ["🍎","🍌","🍇","🍉","🍓","🍒","🥝","🍍"];

// Shuffle function
const shuffle = (array) => [...array].sort(() => Math.random() - 0.5);

const MiniGame = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const playerName = location.state?.playerName || "Player";

  const [cards, setCards] = useState([]);
  const [flipped, setFlipped] = useState([]);
  const [matched, setMatched] = useState([]);
  const [moves, setMoves] = useState(0);
  const [busy, setBusy] = useState(false);

  // Initialize a 4x4 deck
  useEffect(() => {
    const doubleCards = shuffle([...cardSymbols, ...cardSymbols]); // duplicate and shuffle
    setCards(doubleCards);
  }, []);

  const handleFlip = (index) => {
    if (flipped.includes(index) || matched.includes(index) || busy) return;

    const newFlipped = [...flipped, index];
    setFlipped(newFlipped);

    if (newFlipped.length === 2) {
      setMoves((m) => m + 1);
      const [first, second] = newFlipped;

      if (cards[first] === cards[second]) {
        setMatched([...matched, first, second]);
        setFlipped([]);
      } else {
        setBusy(true);
        setTimeout(() => {
          setFlipped([]);
          setBusy(false);
        }, 800);
      }
    }
  };

  // Navigate to result when all matched
  useEffect(() => {
    if (matched.length === cards.length && cards.length > 0) {
      const score = Math.max(0, 100 - moves * 2);
      navigate("/mini-game/result", { state: { playerName, score } });
    }
  }, [matched, cards, moves, playerName, navigate]);

  return (
    <div className="mini-game-intro">
      <h2>Memory Mini-Game</h2>
      <p>Player: {playerName}</p>

      {/* Back button */}
      <div className="button-group" style={{ marginBottom: "1rem" }}>
        <Button baseButton="btn-exit" action={() => navigate("/")} title="Back" />
      </div>

      {/* 4x4 Grid */}
      <div className="emoji-grid">
        {cards.map((symbol, idx) => (
          <div
            key={idx}
            className={`card ${flipped.includes(idx) || matched.includes(idx) ? "flipped" : ""}`}
            onClick={() => handleFlip(idx)}
          >
            <div className="card-inner">
              <div className="card-front">?</div>
              <div className="card-back">{symbol}</div>
            </div>
          </div>
        ))}
      </div>

      <p>Moves: {moves}</p>
    </div>
  );
};

export default MiniGame;
