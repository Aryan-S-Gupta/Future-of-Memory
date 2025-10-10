import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../components/Button/Button.jsx";
import "../styles/MemoryMiniGame.css";

const MiniGameIntro = () => {
  const [playerName, setPlayerName] = useState("");
  const navigate = useNavigate();

  const startGame = () => {
    if (!playerName) return alert("Please enter your name");
    navigate("/mini-game/play", { state: { playerName } });
  };

  return (
    <div className="mini-game-intro">
      <h2>Memory Game</h2>
      <input
        type="text"
        placeholder="Enter your name"
        value={playerName}
        onChange={(e) => setPlayerName(e.target.value)}
      />
      <Button baseButton="btn-primary" action={startGame} title="Start Game" />
    </div>
  );
};

export default MiniGameIntro;
