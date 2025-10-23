import { useState, useEffect, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { getQuestion, submitChoice, getVotingInfo, submitTiebreakScore } from "../../../api/multiplayer/GameFlowApi.js";
import Button from "../../components/Button/Button.jsx";
import { useParams } from "react-router-dom";
import "../../styles/GamePlay.css";
import { useSession } from "../../../SessionContext.jsx";
import background from "../../assets/fallback_first_turn.png";
import { getFunFacts } from "../../../api/single-player/GameApi.js";
import ExitExperience from "../../components/ExitExperience/ExitExperience.jsx";
import BasePage from "../BasePage.jsx";
import LoadingScreen from "../../components/Loading/LoadingScreen.jsx";
import RoomDestroyedPopup from "../../components/RoomDestroy/RoomDestroyedDisplay.jsx";
import MiniGame from "../MiniGame.jsx";

/**
 * PlayerScreen component for multiplayer gameplay.
 * Handles:
 *  - Fetching and displaying questions and scenarios
 *  - Managing player choices and votes
 *  - Handling tie-breaker mini-games
 *  - Integrating background music and text-to-speech narration
 *  - Displaying loading and destroyed room states
 * 
 * @component
 * @returns {JSX.Element} The PlayerScreen view for the current player.
 */
const PlayerScreen = () => {
  const { roomCode, playerName } = useParams();
  const { sessionId } = useSession(); // <-- get session from context
  const [year, setYear] = useState(2035);
  const [screen, setScreen] = useState("scenario"); // "scenario" or "question"
  const [currentTurn, setCurrentTurn] = useState(null);
  const [loadingFacts, setLoadingFacts] = useState([]);
  const [option_id, setOptionId] = useState(null);
  const [turn, setTurn] = useState(-1);
  const [score, setScore] = useState(null);
  const [factsFecthed, setFactsFetched] = useState(false);
  const [miniWinner, setMiniWinner] = useState(null);
  const [miniGameDone, setMiniGameDone] = useState(false);

  // --- Staged reveal for multiplayer ---
  // 0 = nothing, 1 = question, 2 = option1, 3 = option2, 4 = final all
  const [stage, setStage] = useState(0);
  const [hasAnimated, setHasAnimated] = useState(false);
  const [allVoted, setAllVoted] = useState(false);
  const [loadingState, setLoadingState] = useState("none")
  const [scenarioData, setScenarioData] = useState({
    scenario:
    "The year is 2035, and neurotechnology now makes memory manipulation precise and reliable. " +
    "Once experimental, memory editing, enhancement, and storage are mainstream, forcing governments " +
    "to confront choices that could redefine humanity. Nations clash over freedom versus regulation, while corporations drive new concerns around privacy," +
    " ownership, and the commercialization of consciousness.",
    image: background // no image for the first one
  });

  // --- Question Query ---
  // Fetches the question whenever we are on the "question" screen.
  // Fetches the scenario whenever we are on the "scenario" screen.
  const { data: questionData } = useQuery({
    queryKey: ["question", roomCode, sessionId, turn, year],
    queryFn: async () => {
      console.log("queryFn running for", year);
      const result = await getQuestion(sessionId, roomCode, turn, year);
      if (!result) {
        setScreen("loading");
        setLoadingState("question");
        if (!factsFecthed) {
          await fetchFunFacts();
          setFactsFetched(true);
        }
        console("loading at the moment");
        return null;
      } else {
        if (!result.room_exists) {
          setScreen("destroyed");
          return null;
        }
        setCurrentTurn(result);
        setTurn(result.turn_id);
        setScreen("question");
        setLoadingState("none")
        console.log("recieved question data: " + result);
        setScenarioData(null);
        setFactsFetched(false)
        return result;
      }
    }, enabled: loadingState == "question",
    refetchInterval: 3000,
    refetchIntervalInBackground: true,
  })

  const { data: votingData } = useQuery({
    queryKey: ["votingStatus", roomCode, currentTurn?.turn_id],
    queryFn: async () => {
      console.log(
        `[VotingQuery] Fetching voting info for room=${roomCode}, turn=${currentTurn.turn_id}...`
      );
      if (currentTurn === null) return;
      const res = await getVotingInfo(roomCode, currentTurn.turn_id);
      console.log("[VotingQuery] Raw API response:", res);
      const data = res.data
      console.log("[VotingQuery] Parsed data:", res.data);
      console.log("[VotingQuery] onSuccess triggered. Data:", data);
      if (!data) {
        console.log("[VotingQuery] Data empty, skipping state update.");
        return;
      }
      // Map backend vote dictionary → frontend structure
      const mappedVotes = Object.entries(data.votes).map(([player, option]) => ({
        name: player,
        votedFor: option,
        hasVoted: option !== "Pending",
      }));
      console.log(mappedVotes);
      console.log("[VotingQuery] Mapped votes:", mappedVotes);

      const votesCount = data.num_responses;
      const totalCount = data.total_players;

      if (votesCount >= totalCount) {
        setAllVoted(true);
      }

      console.log(
        `[VotingQuery] Vote Progress: ${votesCount}/${totalCount} | All voted? ${allVoted}`
      );
      if (allVoted) {
        console.log("All players voted!");
        if (screen === "miniGame") {
          return null;
        }
        if (data.tie) {  // backend should include this flag
          console.log("Tie detected! Starting mini-game...");
          setScreen("miniGame");
        }
        if (!scenarioData || !scenarioData.scenario) {
          console.log("Scenario not ready → go to loading screen");
          setScreen("loading");
          setLoadingState("scenario");
          if (!factsFecthed) {
            await fetchFunFacts();
            setFactsFetched(true);
          }
        } else {
          setFactsFetched(false);
          console.log("Scenario ready → show scenario");
          setOptionId(data.final_option);
          setScreen("scenario");
        }
      }
      return result;
    }, enabled: screen === "question",
    refetchInterval: 3000,
  })


  // handle choice click
  const handleChoice = async (option_id) => {
    if (!currentTurn) return;
    //setShowVotes(false);
    setOptionId(option_id);
  }

  const {
    data: out,
    isLoading: isTurnLoading,
    error: turnError,
    status: turnStatus,
  } = useQuery({
    queryKey: ["scenario", playerName, roomCode, currentTurn, sessionId, roomCode, option_id, year],
    queryFn: async () => {
      console.log("submitting option", sessionId);
      const out = await submitChoice(playerName, roomCode, sessionId, currentTurn.turn_id, year, option_id);
      console.log(out)
      if (!out || !out.scenario || !out.scenario.text) {
        if (!out.room_exists) {
          setScreen("destroyed");
          return null;
        }
        if (out.tie) {
          console.log("Tie detected! Starting mini-game...");
          setScreen("miniGame");
          return null;
        }
      }
      if (out.tie) {
        console.log("Tie detected! Starting mini-game...");
        setScreen("miniGame");
        return null;
      }
      console.log("the data is", out);
      const mapped = {
        scenario: out.scenario.text,
        image: out.image.url
      };
      console.log("Submit choice response:", mapped);
      setScreen("scenario");
      setFactsFetched(false);
      setScenarioData(mapped);
      setOptionId(null);
      return out;
    },
    enabled: currentTurn != null && option_id != null && screen !== "destroyed" && screen !== "miniGame" && screen !== "miniGameResult" && screen !== "miniGameWaiting",
    onError: (err) => {
      console.log("onError:", err);
    },
    refetchInterval: 3000,
    refetchIntervalInBackground: true,
  });

  // Improved scenario data and year handling to prevent redundant increments
  const scenarioDataRef = useRef(null);
  useEffect(() => {
    if (!scenarioData) return;
    if (scenarioDataRef.current !== null && JSON.stringify(scenarioData) !== JSON.stringify(scenarioDataRef.current)) {
      setYear((prev) => prev + 1);
    }
    scenarioDataRef.current = scenarioData;
  }, [scenarioData]);



  useEffect(() => {
    if (screen === "question") {
      console.log("[Animation] Resetting staged animation for new question");
      setStage(0);
    }
  }, [currentTurn, screen])


  useEffect(() => {
    if (miniGameDone) {
      const handleTiebreak = async () => {
        // Immediately move to waiting screen after finishing mini-game
        setScreen("miniGameWaiting");
        const poll = setInterval(async () => {
          const res = await submitTiebreakScore(playerName, roomCode, turn, score);
          console.log("asking", res);

          if (res.status === "resolved" || res.winner) {
            console.log("Mini-game resolved:", res);
            setMiniWinner(res.winner);
            setScreen("miniGameResult");
            clearInterval(poll);
          }
        }, 2000);

        return () => clearInterval(poll);
      };

      handleTiebreak();
    }
  }, [miniGameDone]);


  useEffect(() => {
    if (screen === "miniGameResult" && miniWinner) {
      const timer = setTimeout(() => {
        setMiniWinner(null);
        setMiniGameDone(false);
        setScreen("loading");
        setLoadingState("scenario");
        fetchFunFacts();
      }, 10000);
      return () => clearTimeout(timer);
    }
  }, [screen, miniWinner]);


  // Fetch fun facts when loading scenario
  const fetchFunFacts = async () => {
    try {
      const facts = await getFunFacts(); // Fetch 3 fun facts
      setLoadingFacts(facts.data);
      console.log("Fun facts loaded:", facts);
    } catch (error) {
      console.error("Error fetching fun facts:", error);
    }
  }

  useEffect(() => {
    if (screen === "question" && currentTurn) setStage(4);
  }, [screen, currentTurn]);



  return (
    <BasePage>
      <ExitExperience code={roomCode} player={playerName} />
      {screen == "destroyed" && (
        <RoomDestroyedPopup />
      )}
      {screen === "loading" && (
        <LoadingScreen
          funFacts={loadingFacts}
          onContinue={() => {
            setScreen({ loadingState });
          }}
        />
      )}
      {screen === "scenario" && scenarioData && (
        <div className="scenario-screen">
          <div className="text-container menu-glass">
            {/* Image in middle */}
            <h2 className="fade-in bigger-text">{scenarioData.scenario}</h2>
          </div>
          {/* Continue button at bottom */}
          <div className="scenario-footer">
            <Button
              baseButton="btn-primary"
              action={() => {
                setScreen("loading");
                setLoadingState("question");
                setAllVoted(false);
                setCurrentTurn(null);
                //setFetchQuestion(true);
                setScenarioData(null);
                console.log("Session ID:", sessionId);
              }}
              title="Continue"
            />
          </div>
        </div>
      )}
      {/** Question Screen*/}
      {screen === "question" && currentTurn && (
        <div className="question-screen">
          {/* Left side: question and choices */}
          <div className="question-main menu-glass">
            <div className="choice-container custom-choices">
              <Button
                baseButton={"choice-btn custom-choice"}
                action={() => handleChoice(currentTurn.options[0].option_id)}
                title={`${currentTurn.options[0].label}. ${currentTurn.options[0].option_text}`}
              />
              <Button
                baseButton={"choice-btn custom-choice"}
                action={() => handleChoice(currentTurn.options[1].option_id)}
                title={`${currentTurn.options[1].label}. ${currentTurn.options[1].option_text}`}
              />
            </div>
          </div>
        </div>
      )}
      {screen === "miniGame" && (
        <MiniGame
          playerName={playerName}
          roomCode={roomCode}
          turnId={turn}
          onFinish={async (score) => {
            console.log(`Mini-game finished with score ${score}`);
            setScore(score)
            setMiniGameDone(true);
          }}
        />
      )}
      {/* === MINI-GAME WAITING (uses mini-wait CSS) === */}
      {screen === "miniGameWaiting" && (
        <div className="mini-wait">
          <h2>⌛ Waiting for Results</h2>
          <p className="text2">Your score has been submitted.</p>
          <p className="text2">Waiting for other players to finish...</p>
        </div>
      )}

      {/* === MINI-GAME WINNER (uses mini-winner CSS) === */}
      {screen === "miniGameResult" && (
        <div className="mini-winner">
          <h2>🏆 Tie Broken!</h2>
          <p className="winner-name">{miniWinner || "Unknown Challenger"}</p>
          <p className="text2">emerges victorious.</p>
        </div>
      )}
    </BasePage>
  );
};



export default PlayerScreen;