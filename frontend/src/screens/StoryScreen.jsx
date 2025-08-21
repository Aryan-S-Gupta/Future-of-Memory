import React from "react";
import Button from "../components/Button/Button";
import { useNavigate } from "react-router-dom";

const StoryScreen = () => {
  const navigate = useNavigate();
  return (
    <div className="text-container">
      <h3>Game Screen</h3>
      <p>Story will be added here later.</p>
      <p>Are you ready for the experience?</p>
      <Button title="Start" baseButton="btn-primary" action={() => navigate("/game-play")} />
    </div>
  );
};

export default StoryScreen;