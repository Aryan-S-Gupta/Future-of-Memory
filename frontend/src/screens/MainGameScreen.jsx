import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import BasePage from "./BasePage.jsx";
import Button from "../components/Button/Button.jsx";
import { createSession } from "../../api/single-player/GameApi.js";
import { useSession } from "../../SessionContext.jsx";
import { Typewriter } from "react-simple-typewriter";
import Screensaver from "../components/Screensaver.jsx";

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
  const { sessionId, setSessionId } = useSession();

  const [showButtons, setShowButtons] = useState(false);

  const [begun, setBegun] = useState(false);

  // Delay to match typing duration (~4.5s)
  useEffect(() => {
    if (!begun) return;
    const timer = setTimeout(() => setShowButtons(true), 4500);
    return () => clearTimeout(timer);
  }, [begun]);

  const start_single_session = async () => {
    try {
      const response = await createSession();
      setSessionId(response.session_id);
      // await startPrerender(sessionId);
      console.log("session is " + sessionId);
      navigate("/story");
    } catch (error) {
      console.error("Error creating single session:", error);
    }
  };

  // const start_multiple_session = async () => {
  //   try {
  //     const response = await createSession();
  //     setSessionId(response.sessionId);
  //     console.log("session is" + sessionId);
  //     navigate("/multiplayer-lobby");
  //   } catch (error) {
  //     console.error("Error creating multiplayer session:", error);
  //   }
  // };

  return (
    <BasePage>
      {/* Screensaver: visible immediately; hides on click; reappears on idle */}
      <Screensaver
        initialShow={true}
        idleMs={600000}
        onDismiss={() => {
          if (!begun) setBegun(true);
        }}
      />

      {/* Game title */}
      <div className={`menu-glass ${showButtons ? "show-buttons" : ""}`}>
        <div className="menu-glass-inner">
          <h1 className="title">
            {begun && (
              <Typewriter
                words={["WELCOME TO", "FUTURE OF MEMORY"]}
                loop={1}
                cursor
                cursorStyle="|"
                typeSpeed={100}
                deleteSpeed={30}
                delaySpeed={1000}
              />
            )}
          </h1>

          {/* Menu buttons */}
          <div className="button-group" aria-hidden={!showButtons}>
            <Button baseButton="btn-primary" action={() => start_single_session()} title="Start" />
            <Button baseButton="btn-primary" action={() => navigate("/multiplayer-lobby")} title="Multiplayer" />
            <Button baseButton="btn-secondary" action={() => navigate("/how-to-play")} title="How To Play" />
            <Button baseButton="btn-secondary" action={() => navigate("/mini-game/intro")} title="Play Memory Game" />
          </div>
          {/* Floating feedback button */}
          <div className="feedback-button-container">
            <Button
              baseButton="btn-feedback"
              action={() => navigate("/feedback")}
              title="Give Feedback"
            />
          </div>
        </div>
      </div>
    </BasePage >
  );
};

export default MainGameScreen;