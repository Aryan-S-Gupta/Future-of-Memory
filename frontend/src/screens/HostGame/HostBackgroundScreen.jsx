import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import BasePage from "../BasePage.jsx";
import Button from "../../components/Button/Button.jsx";
import "../../styles/tokens.css";
import ExitExperience from "../../components/ExitExperience/ExitExperience.jsx";
import { checkGameStarted } from "../../../api/multiplayer/RoomManagementApi.js";
import { startGame } from "../../../api/multiplayer/RoomManagementApi.js";

const HostBackgroundScreen = () => {
  const navigate = useNavigate();
  const { roomCode, playerName, host, mode } = useParams();
  const [gameStarted, setGameStarted] = useState(false);

  const { } = useQuery({
    queryKey: ["started", roomCode],
    queryFn: async () => {
      console.log("Checking whether the game has started...");
      console.log("host is: " + host);
      const res = await checkGameStarted(roomCode);
      if (res.data.game_started) {
        console.log("game started");
        navigate(`/player-room/${roomCode}/${playerName}/${host}/${mode}`);
      }
      return res.data;
    },
    enabled: host !== playerName,  // only run for non-hosts
    refetchInterval: 1000,         // poll every second
    onError: (err) => {
      console.error("Polling error:", err);
    },
  });


  // Host starts game
  const handleStartGame = async () => {
    try {
      await startGame(roomCode)
      setGameStarted(true);
      navigate(`/projector-room/${roomCode}/${playerName}/${host}/${mode}`);
    } catch (err) {
      console.error("Error starting game:", err);
    }
  };

  return (
    <BasePage>
      {mode === "host" && host === playerName && (
        <div>
          <div className="menu-glass howto">
            <div className="menu-glass-inner">
              <h2 className="title">Background</h2>
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
              <Button
                baseButton="btn-primary btn-next next-fade-in"
                action={handleStartGame}
                title={gameStarted ? "Starting..." : "Start Game"}
              />
            </div>
          </div>
          <div className="button-container">
            <ExitExperience code={roomCode} player={playerName} />
          </div>
        </div>
      )}
    </BasePage>)
};

export default HostBackgroundScreen;
