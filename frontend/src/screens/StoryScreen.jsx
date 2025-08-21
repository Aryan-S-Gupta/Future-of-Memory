import React from "react";
import Button from "../components/Button/Button";
import { useNavigate } from "react-router-dom";

const StoryScreen = () => {
  const navigate = useNavigate();
  return (
    <div className="story-screen">
      <h1>Game Screen</h1>
      <p>Story will be added here later.</p>
      <p>Are you ready for the experience?</p>
      <Button title="Start" baseButton="button-primary" action={() => navigate("/game-play")} />
    </div>
  );
};

export default StoryScreen;