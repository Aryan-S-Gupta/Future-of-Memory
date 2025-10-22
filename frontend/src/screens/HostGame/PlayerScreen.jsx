import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { getQuestion, submitChoice } from "../../../api/multiplayer/GameFlowApi.js";
import { getRoomState } from "../../../api/multiplayer/RoomManagementApi.js";
import Button from "../../components/Button/Button.jsx";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import "../../styles/GamePlay.css";
import { useSession } from "../../../SessionContext.jsx";
import background from "../../assets/fallback_first_turn.png";
import { getFunFacts } from "../../../api/single-player/GameApi.js";
import ExitExperience from "../../components/ExitExperience/ExitExperience.jsx";
import BasePage from "../BasePage.jsx";
import { useBgm } from "../../audio/AudioProvider.jsx"; // <-- use bgm state/controls
import { useMemo, useRef } from "react";
import LoadingScreen from "../../components/Loading/LoadingScreen.jsx";
import RoomDestroyedPopup from "../../components/RoomDestroy/RoomDestroyedDisplay.jsx";
import VotingDisplay from "../../components/Voting Display/VotingDisplay.jsx";
import { getVotingInfo } from "../../../api/multiplayer/GameFlowApi.js";
import { getTiebreakStatus } from "../../../api/multiplayer/GameFlowApi.js";
import MiniGame from "../MiniGame.jsx";
import { submitTiebreakScore } from "../../../api/multiplayer/GameFlowApi.js";



const PlayerScreen = () => {
  const navigate = useNavigate()
  const { roomCode, playerName } = useParams();
  const prevQuestionRef = useRef(null);
  const { sessionId } = useSession(); // <-- get session from context
  const [year, setYear] = useState(2035);
  const [screen, setScreen] = useState("scenario"); // "scenario" or "question"
  const [currentTurn, setCurrentTurn] = useState(null);
  const [loadingFacts, setLoadingFacts] = useState([]);
  const [isReady, setIsReady] = useState(false);
  const [option_id, setOptionId] = useState(null);
  const [turn, setTurn] = useState(-1);
  const [votes, setVotes] = useState([]);
  const [totalPlayers, setTotalPlayers] = useState(1);
  const [score, setScore] = useState(null);
  const [factsFecthed, setFactsFetched] = useState(false);
  const [miniWinner, setMiniWinner] = useState(null);
  const [miniGameDone, setMiniGameDone] = useState(false);

  // --- Staged reveal for multiplayer ---
  // 0 = nothing, 1 = question, 2 = option1, 3 = option2, 4 = final all
  const [stage, setStage] = useState(0);
  const [hasAnimated, setHasAnimated] = useState(false);
  const fadeDuration = 2000;
  const [allVoted, setAllVoted] = useState(false);
  const [loadingState, setLoadingState] = useState("none")
  const [scenarioData, setScenarioData] = useState({
    scenario:
      "The year is 2035, and neurotechnology now makes memory manipulation precise and reliable. " +
      "Once experimental, memory editing, enhancement, and storage are mainstream, forcing governments " +
      "to confront choices that could redefine humanity. manipulation not just possible, but precise and reliable." +
      "Memory editing, enhancement," +
      "These technologies can erase trauma, boost learning, and even share memories, offering both promise " +
      "and peril. Nations clash over freedom versus regulation, while corporations drive new concerns around privacy," +
      " ownership, and the commercialization of consciousness.",
    image: background // no image for the first one
  });



  // --- Tie narration to BGM ---
  const { isPlaying, isMuted, volume, setVolume } = useBgm();


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
    refetchInterval: (result) => result ? false : 3000,
    refetchIntervalInBackground: true,
  })



  // --- Minimal TTS: inline (match single-player volume/mute) ---
  const synthRef = useRef(typeof window !== "undefined" ? window.speechSynthesis : null);
  const prevVolRef = useRef(null);
  const duckFactor = 0.3;

  const cancelTTS = () => {
    try { synthRef.current?.cancel(); } catch { }
    if (prevVolRef.current !== null) {
      setVolume(prevVolRef.current);
      prevVolRef.current = null;
    }
  };

  const speak = (text, onDone) => {
    if (!synthRef.current || !text) {
      if (typeof onDone === "function") onDone();
      return;
    }
    // stop previous
    cancelTTS();

    // Only narrate if BGM is playing
    if (!isPlaying) {
      if (typeof onDone === "function") onDone();
      return;
    }

    // duck BGM
    prevVolRef.current = volume;
    setVolume(Math.max(0, Math.min(1, volume * duckFactor)));

    const utter = new SpeechSynthesisUtterance(String(text));
    const voices = synthRef.current.getVoices();
    const prefs = [
      /Microsoft Sonia Online \(Natural\).*English \(United Kingdom\)/i,
      /Microsoft Jenny Online \(Natural\).*English \(United States\)/i,
      /Samantha/i, /Victoria/i, /Serena/i, /Daniel/i,
      /Google UK English Female/i
    ];
    const picked = prefs.map(rx => voices.find(v => rx.test(v.name))).find(Boolean) || voices[0];
    if (picked) utter.voice = picked;

    // match SP params
    utter.rate = 0.7;
    utter.pitch = 1.0;
    utter.volume = isMuted ? 0 : Math.max(0, Math.min(1, volume));

    const restore = () => {
      if (prevVolRef.current !== null) {
        setVolume(prevVolRef.current);
        prevVolRef.current = null;
      }
      if (typeof onDone === "function") onDone();
    };

    utter.onend = restore;
    utter.onerror = restore;

    try { synthRef.current.speak(utter); } catch { restore(); }
  };


  // Auto-read Scenario when it shows (and BGM is playing)
  useEffect(() => {
    if (screen === "scenario" && scenarioData?.scenario) {
      speak(scenarioData.scenario);
    }
    return () => cancelTTS();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [screen, scenarioData?.scenario, isPlaying]); // tie to playing state

  useEffect(() => {
    const handler = () => {
      if (screen === "scenario" && scenarioData?.scenario) {
        speak(scenarioData.scenario);
      } else if (screen === "question" && currentTurn) {
        if (stage === 2) speak(currentTurn?.options?.[0]?.option_text);
        else if (stage === 3) speak(currentTurn?.options?.[1]?.option_text);
      }
    };
    window.addEventListener("bgm-play", handler);
    return () => window.removeEventListener("bgm-play", handler);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [screen, scenarioData?.scenario, currentTurn, stage, isPlaying]);


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
      setVotes(mappedVotes);
      setTotalPlayers(data.total_players);
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
    cancelTTS();
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
      setScenarioData(mapped);
      setYear(year + 1);
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



  useEffect(() => {
    if (screen === "question") {
      console.log("[Animation] Resetting staged animation for new question");
      setHasAnimated(false);
      setStage(0);
    }
  }, [currentTurn, screen])


  // --- Staged reveal ---
  // 0 = nothing, 1 = question, 2 = option1, 3 = option2, 4 = final all

  const fadeBase = 1000; // align with SP fade
  useEffect(() => {
    if (screen !== "question" || !currentTurn) return;

    // Start with question stage visible (for timing parity), but don't speak it
    setStage(1);

    const optA = currentTurn?.options?.[0]?.option_text;
    const optB = currentTurn?.options?.[1]?.option_text;

    const t1 = setTimeout(() => {
      setStage(2);                    // show A
      if (optA) speak(optA);
    }, 12000 - fadeBase);

    const t2 = setTimeout(() => {
      setStage(3);                    // show B
      if (optB) speak(optB);
    }, 18000 - fadeBase);

    const t3 = setTimeout(() => {
      setStage(4);                    // show all
    }, 24000 - fadeBase);

    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); cancelTTS(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [screen, currentTurn, isPlaying]);


  const getFadeClass = (idx) => {
    switch (idx) {
      case 1: return stage === 1 || stage === 4 ? "fade-in-out show" : stage > 1 ? "fade-in-out hide" : "fade-in-out";
      case 2: return stage === 2 || stage === 4 ? "fade-in-out show" : stage > 2 ? "fade-in-out hide" : "fade-in-out";
      case 3: return stage === 3 || stage === 4 ? "fade-in-out show" : stage > 3 ? "fade-in-out hide" : "fade-in-out";
      default: return "fade-in-out";
    }
  };

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



  return (
    <BasePage>
      <ExitExperience code={roomCode} player={playerName} />
      {screen == "destroyed" && (
        <RoomDestroyedPopup />
      )}
      {screen === "loading" && (
        <LoadingScreen
          isReady={isReady}
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
                baseButton={getFadeClass(2) + " choice-btn custom-choice"}
                action={() => handleChoice(currentTurn.options[0].option_id)}
                title={`${currentTurn.options[0].label}. ${currentTurn.options[0].option_text}`}
              />
              <Button
                baseButton={getFadeClass(3) + " choice-btn custom-choice"}
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