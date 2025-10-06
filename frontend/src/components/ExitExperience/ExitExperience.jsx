import { useNavigate } from "react-router-dom";
import { useState } from "react";
import "../../styles/ExitExperience.css"; 
import Button from "../Button/Button.jsx";
import { leaveRoom } from "../../../api/multiplayer/RoomManagementApi.js";
import RoomDestroyedPopup from "../RoomDestroy/RoomDestroyedDisplay.jsx";

const ExitExperience = ({code, player}) => {
  const navigate = useNavigate();
  const [showPopup, setShowPopup] = useState(false);

  const exitRoom = async() => {
    console.log(code)
    console.log(player)
    if (code == "-1" && player == "single-player") {
      navigate("/")
      return
    } else {
      const res = await leaveRoom(code, player)
      if (!res.success) {
        if (!res.room_exists) {
                  navigate("/")
          //return;
          //setRoomDestroyed(true);
          // handle room doesnt exist
        }
        console.log("leaving room was not successful: " + res.message);
      } else {
        console.log(player + " has left the room with room code " + code)
        navigate("/")
      }
    }
  }
  return (
    <div>
      {/* Exit button pinned to top-right */}
      <Button 
        baseButton="btn-exit" 
        action={() => setShowPopup(true)} 
        title="Exit Experience"  
      />

      {showPopup && (
        <div className="popup-overlay">
          <div className="popup-box">
            <h2>Are you sure you want to exit the experience?</h2>
            <div className="popup-actions">
              <button className="btn-confirm" onClick={() => exitRoom()}>
                Yes, Exit
              </button>
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
