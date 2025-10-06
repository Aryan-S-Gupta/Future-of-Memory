import { useNavigate } from "react-router-dom";
import { useState } from "react";
import "../../styles/ExitExperience.css"; 
import Button from "../Button/Button.jsx";

const ExitExperience = () => {
  const navigate = useNavigate();
  const [showPopup, setShowPopup] = useState(false);

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
              <button className="btn-confirm" onClick={() => navigate("/")}>
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
