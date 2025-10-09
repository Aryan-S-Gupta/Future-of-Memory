import React from "react";
import "../../styles/RoomDestroyedPopup.css"; // Make sure this CSS file contains your updated styles
import { useNavigate } from "react-router-dom";

const RoomDestroyedPopup = () => {
    const navigate = useNavigate();
  return (
    <div className="popup-overlay">
      <div className="popup-box">
        <h2>Room Destroyed</h2>
        <p>The host has left, and this room no longer exists.</p>

        <div className="popup-actions">

            <button className="btn-confirm" onClick={() => navigate("/multiplayer-lobby")}>
              Join a Different Room
            </button>
      
            <button className="btn-cancel" onClick={() => navigate("/")}>
              Exit
            </button>
  
        </div>
      </div>
    </div>
  )
}

export default RoomDestroyedPopup;