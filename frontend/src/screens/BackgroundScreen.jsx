import { useNavigate } from "react-router-dom";
import BasePage from "./BasePage.jsx";
import Button from "../components/Button/Button.jsx";
import "../styles/tokens.css";
import ExitExperience from "../components/ExitExperience/ExitExperience.jsx";
import { startPrerender } from "../../api/single-player/GameApi.js";
import { useSession } from "../../SessionContext.jsx";

/**
 * BackgroundScreen component
 *
 * This screen introduces the narrative background of the game.
 * It provides immersive story context before gameplay begins, 
 * styled with a "crawl" effect (scrolling text).
 *
 * Features:
 * - Narrative text explaining the year 2040 and the player's role.
 * - A "Back" button to return to the home screen.
 * - A "Next" button to proceed into the GamePlay screen.
 *
 * @component
 * @returns {JSX.Element} A styled introductory background screen with story text and navigation.
 */
const BackgroundScreen = () => {
  const navigate = useNavigate();
  const { sessionId } = useSession();

  const start = async () => {
    await startPrerender(sessionId);
    navigate("/game-play");
  }
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
          <Button baseButton="btn-primary btn-next next-fade-in" action={start} title="Next" />
        </div>
      </div>

      {/* Navigation buttons (Back to home, Next to gameplay) */}
      <div className="button-container">
        <ExitExperience />
      </div>
    </BasePage>
  );
};
export default BackgroundScreen;
