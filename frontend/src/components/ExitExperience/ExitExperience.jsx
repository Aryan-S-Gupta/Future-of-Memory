
import { useNavigate } from "react-router-dom";
import { useState } from "react";

import "../../styles/ExitExperience.css"; 
import Button from "../Button/Button.jsx";
import { leaveRoom } from "../../../api/multiplayer/RoomManagementApi.js";
import RoomDestroyedPopup from "../RoomDestroy/RoomDestroyedDisplay.jsx";

// Component handles the "Exit Experience" button and confirmation popup
const ExitExperience = ({ code, player }) => {
  // Used to redirect user to a different route
  const navigate = useNavigate();
  // Controls visibility of confirmation popup
  const [showPopup, setShowPopup] = useState(false);

  // Function called when user confirms they want to exit
  const exitRoom = async () => {
    console.log(code);
    console.log(player);

    // Case 1: Single-player mode → no API call needed
    if (code == "-1" && player == "single-player") {
      navigate("/");
      console.log("exited successfully");
      return null;
    } 
    // Case 2: Multiplayer mode → call API to leave room
    else {
      // Attempt to leave room via backend
      const res = await leaveRoom(code, player); 

      // If leaving the room failed
      if (!res.success) {
        // If the room no longer exists, just return to home
        if (!res.room_exists) {
          navigate("/");
        }
        console.log("Leaving room was not successful: " + res);
      } 
      // If leaving was successful
      else {
        console.log(`${player} has left the room with room code ${code}`);
        navigate("/"); // Redirect to home screen
      }
    }
  };

  return (
    <div>
      {/* Exit button pinned to top-right corner */}
      <Button 
        baseButton="btn-exit" 
        action={() => setShowPopup(true)} // Show popup when user clicks exit
        title="Exit Experience"  
      />

      {/* Confirmation popup (renders only when showPopup is true) */}
      {showPopup && (
        <div className="popup-overlay">
          <div className="popup-box">
            <h2>Are you sure you want to exit the experience?</h2>
            <div className="popup-actions">
              {/* Confirm exit button */}
              <button className="btn-confirm" onClick={() => exitRoom()}>
                Yes, Exit
              </button>

              {/* Cancel exit button */}
              <button className="btn-cancel" onClick={() => setShowPopup(false)}>
                No, Stay
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExitExperience;
