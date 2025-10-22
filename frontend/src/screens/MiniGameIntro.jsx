import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import BasePage from "./BasePage.jsx";
import Button from "../components/Button/Button.jsx";
import ExitExperience from "../components/ExitExperience/ExitExperience.jsx";
import "../styles/tokens.css";
import "../styles/MemoryMiniGame.css";

const MiniGameIntro = () => {
  const [playerName, setPlayerName] = useState("");
  const navigate = useNavigate();

  const startGame = () => {
    if (!playerName) return alert("Please enter your name");
    navigate("/mini-game/play", { state: { playerName } });
  };

  return (
    <BasePage>
      <div className="menu-glass howto mini-intro">
        <div className="menu-glass-inner">
          <h2 className="title">Memory Game</h2>

          <div className="intro-form">
            <label htmlFor="playerName" className="sr-only">Player name</label>
            <input
              id="playerName"
              className="intro-input"
              type="text"
              placeholder="Enter your name"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
            />

            <div className="intro-actions">
              <Button
                baseButton="btn-primary"
                action={startGame}
                title="Start Game"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Left/back control exactly like BackgroundScreen */}
      <div className="button-container">
        <ExitExperience />
      </div>
    </BasePage>
  );
};

export default MiniGameIntro;
