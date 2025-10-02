import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import BasePage from "./BasePage.jsx";
import Button from "../components/Button/Button.jsx";
import "../styles/BackgroundScreen.css";
import ExitExperience from "../components/ExitExperience/ExitExperience.jsx";

/**
 * BackgroundScreenMulti component
 *
 * Multiplayer background intro before gameplay begins.
 * Just shows the story crawl, no API calls needed.
 */
const BackgroundScreenMulti = () => {
  const navigate = useNavigate();
  const { roomCode } = useParams();
  const [searchParams] = useSearchParams();
  const playerName = searchParams.get("playerName");

  const goToGame = () => {
    navigate(`/game-play-multi/${roomCode}?playerName=${playerName}`);
  };

  return (
    <BasePage>
      <h1 className="title">Background</h1>

      {/* Story crawl container with immersive narrative */}
      <div className="crawl-container">
        <div className="crawl-text">
          <p>
            Welcome to 2035 <br /> <br />
            Where neurotechnology connects minds, rewrites memories, and reshapes reality. <br /> <br />
            Together with other leaders, you stand between promise and peril. <br /> <br />
            Every decision you debate and every law you pass will ripple across nations,              
            redefining what it means to be human. <br /> <br />
            Will you forge alliances, push for progress, or defend your people’s values? <br /> <br />
            The destiny of millions rests in your collective hands! <br /> <br />  
          </p>
        </div>
      </div>

      {/* Navigation buttons */}
      <div className="button-container">
        <ExitExperience />
        <Button 
          baseButton="btn-next next-fade-in" 
          action={goToGame} 
          title="Next" 
        />
      </div>
    </BasePage>
  );
};

export default BackgroundScreenMulti;