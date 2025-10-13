import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import BasePage from "./BasePage.jsx";
import Button from "../components/Button/Button.jsx";
import "../styles/tokens.css";
import ExitExperience from "../components/ExitExperience/ExitExperience.jsx";

/**
 * BackgroundScreenMulti component
 *
 * Multiplayer background intro before gameplay begins.
 * Just shows the story crawl, no API calls needed.
 */
const BackgroundScreenMulti = () => {
  const navigate = useNavigate();
  const { roomCode, playerName } = useParams();
  const goToGame = () => {
    navigate(`/multiplayer-room/${roomCode}/${playerName}`);
  };

  return (
    <BasePage>
      <div className="menu-glass howto">
        <div className="menu-glass-inner">
          <h2 className="title">Background</h2>
          <div className="crawl-container">
            <div className="crawl-text">
              <p>
                Welcome to 2035 <br /> <br />
                Where neurotechnology connects minds, rewrites memories, and reshapes reality. <br /> <br />
                You are the chosen voice of your people, standing between promise and peril.  <br /> <br />
                Every law you shape will ripple through lives and futures,
                redefining what it means to be human.<br /> <br />
                Will you shield your community, pursue progress, or uphold your ethics? <br /> <br />
                The destiny of millions rests in your hands! <br /> <br />
              </p>
            </div>
          </div>
          <Button baseButton="btn-confirm btn-next next-fade-in" action={goToGame} title="Next" />
        </div>
      </div>

      {/* Navigation buttons */}
      <div className="button-container">
        <ExitExperience code={roomCode} player={playerName} />
      </div>
    </BasePage>
  );
};

export default BackgroundScreenMulti;