import { useNavigate } from "react-router-dom";
import BasePage from "../components/BasePage/BasePage.jsx";
import Button from "../components/Button/Button.jsx";
import "./BackgroundScreen.css";
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
  const { session } = useSession();

  const pre_render = async () => {
    await startPrerender(session, "2035");
    navigate("/game-play");
  }
  return (
    <BasePage>
      <h1 className="title">Background</h1>
        {/* Story crawl container with immersive narrative */}
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
      {/* Navigation buttons (Back to home, Next to gameplay) */}
      <div className="button-container">
      <Button baseButton="btn-back" action={() => navigate("/")} title="Back" />
      <Button baseButton="btn-next next-fade-in" action={() => pre_render()} title="Next" />
      </div>
      </BasePage>
    );
};
export default BackgroundScreen;
