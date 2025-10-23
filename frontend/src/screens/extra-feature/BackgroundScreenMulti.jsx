import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import BasePage from "../BasePage.jsx";
import Button from "../../components/Button/Button.jsx";
import "../../styles/tokens.css";
import ExitExperience from "../../components/ExitExperience/ExitExperience.jsx";

/**
 * This screen serves as the introductory background for multiplayer sessions in "Future of Memory."
 * It is shown to the **host** before the game officially starts and allows them to initiate the session.
 * For **non-host** players, it continuously polls the backend to check whether the game has begun.
 *
 * Features:
 * - Displays a narrative "crawl" introduction setting the story context for 2035.
 * - Host can start the multiplayer session once all players are ready.
 * - Non-hosts automatically transition to the player room once the host starts the game.
 * - Includes a modal alert if the host attempts to start the game with an empty room.
 * - Integrates with `ExitExperience` for users to safely exit the session.
 *
 * Routing Parameters (from `useParams`):
 * - `roomCode`: The unique identifier for the multiplayer room.
 * - `playerName`: The current player's display name.
 * - `host`: The designated host's name.
 * - `mode`: Game mode (e.g., "host" or "player").
 *
 * Dependencies:
 * - React hooks (`useState`, `useEffect`)
 * - React Router (`useNavigate`, `useParams`)
 * - React Query (`useQuery`) for backend polling
 * - `BasePage` layout wrapper
 * - `Button` and `ExitExperience` components
 * - API calls: `checkGameStarted`, `startGame`
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
          <Button baseButton="btn-primary btn-next next-fade-in" action={goToGame} title="Next" />
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