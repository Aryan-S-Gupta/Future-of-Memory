import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Button from "../components/Button/Button.jsx";
import { submitMemoryScore } from "../../api/multiplayer/GameFlowApi.js";
import "../styles/MemoryMiniGame.css";

const MiniGameResult = () => {
  const { state } = useLocation();
  const navigate = useNavigate();
  const playerName = state?.playerName;
  const score = state?.score;

  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!playerName || score == null) return;

    const submitScore = async () => {
      try {
        const res = await submitMemoryScore(playerName, score);
        console.log("Score submitted:", res);
        setSubmitted(true);
      } catch (err) {
        console.error("Failed to submit score:", err);
        setError("Failed to submit score. Please try again.");
      }
    };

    submitScore();
  }, [playerName, score]);

  return (
    <div className="menu-glass">
      <div className="menu-glass-inner">
        <div className="mini-game-result">
          <h2>Well Done, {playerName}!</h2>
          <p>Your Score: {score}</p>

          {error && <p style={{ color: "red" }}>{error}</p>}
          {!submitted && !error && <p>Submitting your score...</p>}

          <Button
            baseButton="btn-primary"
            action={() => navigate("/")}
            title="Back to Menu"
          />
        </div>
      </div>
    </div>
  );
};

export default MiniGameResult;
