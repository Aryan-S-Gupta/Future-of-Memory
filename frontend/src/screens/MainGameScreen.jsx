import { useNavigate } from "react-router-dom";
import BasePage from "./BasePage.jsx";
import Button from "../components/Button/Button.jsx";
import { Typewriter } from "react-simple-typewriter";

/**
 * MainGameScreen component
 *
 * This is the game's main menu screen.
 * It acts as the entry point where the player can:
 *  - Start the interactive story
 *  - View instructions on how to play
 *
 * Features:
 * - Uses `BasePage` to provide consistent layout with background styling.
 * - Provides navigation buttons for starting the story or viewing instructions.
 *
 * @component
 * @returns {JSX.Element} The main game menu screen with navigation options.
 */
const MainGameScreen = () => {
  // Hook for navigation between routes
  const navigate = useNavigate();

  return (
    <BasePage>
      {/* Game title */}
      <h1 className="title">
        <Typewriter
          words={["WELCOME TO", "FUTURE OF MEMORY"]}
          loop={1}              // run through once
          cursor
          cursorStyle="|"
          typeSpeed={100}
          deleteSpeed={30}
          delaySpeed={1000}     // pause before deleting
        />
      </h1>

      {/* Menu buttons */}
      <div className="button-group">
        <Button baseButton="btn-primary" action={() => navigate("/story")} title="Start" />
        <Button baseButton="btn-secondary" action={() => navigate("/how-to-play")} title="How To Play" />
      </div>
    </BasePage>
  );
};

export default MainGameScreen;
