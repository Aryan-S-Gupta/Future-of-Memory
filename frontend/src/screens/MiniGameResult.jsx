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

  return (
    <div className="menu-glass">
      <div className="menu-glass-inner">
        <div className="mini-game-result">
          <h2>Well Done, {playerName}!</h2>
          <p>Your Score: {score}</p>


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
