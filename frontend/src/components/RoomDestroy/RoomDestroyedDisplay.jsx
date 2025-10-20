import "../../styles/RoomDestroyedPopup.css"; 
import { useNavigate } from "react-router-dom";


/**
 * RoomDestroyedPopup Component
 * 
 * This component displays a popup notification when a multiplayer room 
 * has been destroyed — typically when the host leaves the room. 
 * 
 * The popup informs the player that the room no longer exists and 
 * provides two navigation options:
 * - Join a different room (navigates to the multiplayer lobby)
 * - Exit back to the home page
 * 
 * @component
 * @returns {JSX.Element} The rendered RoomDestroyedPopup component.
 */
const RoomDestroyedPopup = () => {
    const navigate = useNavigate();
  return (
    // Overlay background to dim rest of the screen
    <div className="popup-overlay">
      <div className="popup-box">
        <h2>This room is no longer available.</h2>
        <p>The host or all players have left, so the room has been closed.</p>

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