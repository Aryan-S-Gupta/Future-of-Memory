import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { getQuestion, submitChoice } from "../../../api/multiplayer/GameFlowApi.js";
import { getRoomState } from "../../../api/multiplayer/RoomManagementApi.js";
import Button from "../../components/Button/Button.jsx";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import "../../styles/GamePlay.css";
import { useSession } from "../../../SessionContext.jsx";
import background from "../../assets/background.jpg";
import { getFunFacts } from "../../../api/single-player/GameApi.js";
import ExitExperience from "../../components/ExitExperience/ExitExperience.jsx";
import BasePage from "../BasePage.jsx";
import { useBgm } from "../../audio/AudioProvider.jsx"; // <-- use bgm state/controls
import { useMemo, useRef } from "react";
import LoadingScreen from "../../components/Loading/LoadingScreen.jsx";
import RoomDestroyedPopup from "../../components/RoomDestroy/RoomDestroyedDisplay.jsx";
import VotingDisplay from "../../components/Voting Display/VotingDisplay.jsx";
import { getVotingInfo} from "../../../api/multiplayer/GameFlowApi";
import MiniGame from "../MiniGame.jsx";
import { submitTiebreakScore } from "../../../api/multiplayer/GameFlowApi.js";

/**
 * furs duspay the questions and after the the players have submiyyed the responses then go to the loading screen
 * until the scenario and the image is ready ad once ready display the mimage and set current turn to null so that 
 * the new data can be stored 
 * to ftech 
 * 
 * MINI GAME LOGIC: 
 * once submit response results in tie then set the screen to mini game on players.
 * if it is host (host will be checked by playerName = hostName) then display 
 * "Tie detected.. starting mini competition.. lets seee whose memort is the mosyt powerful" +
 * keep checking whetehr mini game has been resolved or who has finished
 * once resolved, display on host who the winner is for 10 seconds and then set the screen back to scenario 
 * if the scenario is not ready then loading;
 */

const HostScreen = () => {
  const navigate = useNavigate()
  const { roomCode, playerName } = useParams(); 
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
  const [miniGameOccurred, setMiniGameOccurred] = useState(false);
  const [winnerInfo, setWinnerInfo] = useState(null);
  const [showWinner, setShowWinner] = useState(false);
  const [played, setPlayed] = useState(false)
  const [factsFecthed, setFactsFetched] = useState(false);

  // --- Staged reveal for multiplayer ---
  // 0 = nothing, 1 = question, 2 = option1, 3 = option2, 4 = final all
  const [stage, setStage] = useState(0);
  
  const [hasAnimated, setHasAnimated] = useState(false); 
  const fadeDuration = 2000;
  const [allVoted, setAllVoted] = useState(false);
  const [loadingState, setLoadingState] = useState("none")
  const [tieMode, setTieMode] = useState(false);
  const [tieStatus, setTieStatus] = useState(null);
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
  const [roomDestroyed, setRoomDestroyed] = useState(false);



  // --- Tie narration to BGM ---
  const { isPlaying, volume, setVolume } = useBgm();


  // --- Question Query ---
  // Fetches the question whenever we are on the "question" screen.
  const {data: questionData} = useQuery ({
    queryKey: ["question", roomCode, sessionId, turn, year], 
    queryFn: async() => {
        console.log("queryFn running for", year);
        const result = await getQuestion(sessionId, roomCode, turn , year);
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
          setCurrentTurn(result);
          setTurn(result.turn_id);
          setScreen("question");
          setLoadingState("none")
          console.log("recieved question data: " + result);
          setScenarioData(null);
          setFactsFetched(false);
          return result;
        }
    }, enabled: loadingState == "question", 
      refetchInterval: (result) => result ? false : 3000,
    refetchIntervalInBackground: true, 
  })


  const {} = useQuery({
    queryKey: ["votingStatus", roomCode, currentTurn?.turn_id], 
    queryFn: async() => {
        
      console.log(`[VotingQuery] Fetching voting info for room=${roomCode}, turn=${currentTurn.turn_id}`);

        if (currentTurn === null) return;
        const res = await getVotingInfo(roomCode, currentTurn.turn_id);
        const data = res.data
        
        console.log("[VotingQuery] Raw API response:", res);
        console.log("[VotingQuery] Parsed data:", res.data);
        console.log("[VotingQuery] onSuccess triggered. Data:", data);
        
        if (!data) {
          console.log("[VotingQuery] Data empty, skipping state update.");
          return;
        }
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

      if (data.tie) {
        console.log("Tie detected! Starting mini-game round...");
        setTieMode(true);
        setScreen("miniGameWait");
        return;
      }



        console.log(`[VotingQuery] Vote Progress: ${votesCount}/${totalCount} | All voted? ${allVoted}`);
        if (allVoted) {
          console.log("All players voted!");
          setOptionId(data.final_option);
          if (!scenarioData || !scenarioData.scenario) {
            console.log("Scenario not ready → go to loading screen");
            setScreen("loading");
            setLoadingState("scenario");
            if (!factsFecthed) {
              await fetchFunFacts();
            }
          } else {
            console.log("Scenario ready → show scenario");
            setScreen("scenario");
            setLoadingState("none")
          }
        }
        return result;
      }, enabled: screen == "question" && currentTurn != null,
      refetchInterval: 3000,
      refetchIntervalInBackground: true
  })


  const {} = useQuery({
      queryKey: ["scenario", playerName, roomCode, currentTurn, sessionId, roomCode, option_id, year],
      queryFn: async () => {

        console.log("submitting option", option_id);

        const out = await submitChoice(playerName, roomCode, sessionId,currentTurn.turn_id, year, option_id);
        console.log(out)
        if (!out || !out.scenario || !out.scenario.text) {
          if (!out.room_exists) {
            setRoomDestroyed(true); 
            setScreen("destroyed");
          }
        }
        console.log("the data is", out );

        const mapped = {
          scenario: out.scenario.text,
          image: out.image.url
        };
        console.log("Submit choice response:", mapped);

        setScreen("scenario");
        setLoadingState("none")
        setScenarioData(mapped);
        setYear(year + 1);
        setOptionId(null);
        return out;
      },
      enabled: currentTurn != null &&  option_id != null && screen !== "destroyed",
      onError: (err) => {
        console.log("onError:", err);
      }, 
      refetchInterval: 3000, 
      refetchIntervalInBackground: true, 
  });

  const {} = useQuery({
  queryKey: ["tiebreakStatus", roomCode, currentTurn?.turn_id],
  queryFn: async () => {
    if (!tieMode || !currentTurn) return;
    const res = await getTiebreakStatus(roomCode, currentTurn.turn_id);
    console.log("[TIEBREAK STATUS]", res);

    if (res.status === "resolved" || res.winner) {
      setWinnerInfo(res);
      setScreen("miniGameWinner");
      setTimeout(() => {
        setTieMode(false);
        setScreen("loading");
        setLoadingState("scenario");
      }, 10000);
    }
    return res;
  },
  enabled: tieMode && currentTurn != null,
  refetchInterval: 2000,
});



  // --- Minimal TTS: inline (no extra files/deps) ---
  const synthRef = useRef(typeof window !== "undefined" ? window.speechSynthesis : null);
  const prevVolRef = useRef(null); // remember user volume while narrating
  const duckFactor = 0.3; // simple lower (no separate ducking state)

  const cancelTTS = () => {
    try { synthRef.current?.cancel(); } catch { }
    // Restore volume if we changed it
    if (prevVolRef.current !== null) {
      setVolume(prevVolRef.current);
      prevVolRef.current = null;
    }
  };

  const speak = (text) => {
    if (!synthRef.current || !text) return;
    // Cancel any previous narration
    cancelTTS();

    // Only narrate if BGM is playing (toolbar controls this)
    if (!isPlaying) return;

    // Lower BGM volume temporarily (minimal approach)
    prevVolRef.current = volume;
    setVolume(Math.max(0, Math.min(1, volume * duckFactor)));

    const utter = new SpeechSynthesisUtterance(String(text));
    // --- choose voice here ---
    const voices = synthRef.current.getVoices();
    const prefs = [
      /Microsoft Sonia Online \(Natural\).*English \(United Kingdom\)/i, // Edge (neural)
      /Microsoft Jenny Online \(Natural\).*English \(United States\)/i,  // Edge (neural)
      /Samantha/i, /Victoria/i, /Serena/i, /Daniel/i,                    // macOS built-ins
      /Google UK English Female/i                                        // Chrome fallback
    ];
    const picked = prefs
      .map(rx => voices.find(v => rx.test(v.name)))
      .find(Boolean) || voices[0];
    utter.voice = picked;
    // tweak for more “majestic” feel
    utter.rate = 0.90;  // slower = more weighty
    utter.pitch = 1.12;  // deeper
    utter.volume = 1;   // full, since we ducked bgm


    utter.onend = utter.onerror = () => {
      // Restore BGM volume
      if (prevVolRef.current !== null) {
        setVolume(prevVolRef.current);
        prevVolRef.current = null;
      }
    };


    try { synthRef.current.speak(utter); } catch {
      // In case of any error, restore
      if (prevVolRef.current !== null) {
        setVolume(prevVolRef.current);
        prevVolRef.current = null;
      }
    }
  };

  // Build readout for question + options
  const questionReadout = useMemo(() => {
    if (!questionData) return "";
    const q = String(questionData.question || "");
    const alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const parts = Object.entries(questionData.options || {}).map(
      ([, text], i) => `Option ${alpha[i] || i + 1}: ${String(text)}`
    );
    return [q, ...parts].join(". ");
  }, [questionData]);


  // Auto-read Scenario when it shows (and BGM is playing)
  useEffect(() => {
    if (screen === "scenario" && scenarioData?.scenario) {
      speak(scenarioData.scenario);
    }
    return () => cancelTTS();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [screen, scenarioData?.scenario, isPlaying]); // tie to playing state


  // Auto-read Question + Options when it shows (and BGM is playing)
  useEffect(() => {
    if (screen === "question" && questionReadout) {
      speak(questionReadout);
    }
    return () => cancelTTS();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [screen, questionReadout, isPlaying]);


  // Replay narration when toolbar Play is clicked (even if already playing)
  useEffect(() => {
    const handler = () => {
      if (screen === "scenario" && scenarioData?.scenario) {
        speak(scenarioData.scenario);
      } else if (screen === "question" && questionReadout) {
        speak(questionReadout);
      }
    };
    window.addEventListener("bgm-play", handler);
    return () => window.removeEventListener("bgm-play", handler);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [screen, scenarioData?.scenario, questionReadout, isPlaying]);


useEffect(() => {
  if (screen === "question") {
    console.log("[Animation] Resetting staged animation for new question");
    setHasAnimated(false);
    setStage(0);
  }
}, [currentTurn, screen])


// --- Staged reveal ---
  // 0 = nothing, 1 = question, 2 = option1, 3 = option2, 4 = final all
 
  useEffect(() => {
    if (screen === "question" && currentTurn) {
      setStage(1); // show question
      speak(currentTurn.question);


      const timer1 = setTimeout(() => {
        setStage(2);
        speak(currentTurn.options[0].option_text);
      }, 10000 - fadeDuration);


      const timer2 = setTimeout(() => {
        setStage(3);
        speak(currentTurn.options[1].option_text);
      }, 15000 - fadeDuration);


      const timer3 = setTimeout(() => {
        setStage(4); // show all together, no TTS
      }, 20000 - fadeDuration);


      return () => {
        clearTimeout(timer1);
        clearTimeout(timer2);
        clearTimeout(timer3);
        cancelTTS();
      };
    }
  }, [screen, currentTurn]);


const getFadeClass = (idx) => {
  switch(idx) {
    case 1: return stage === 1 || stage === 4 ? "fade-in-out show" : stage > 1 ? "fade-in-out hide" : "fade-in-out";
    case 2: return stage === 2 || stage === 4 ? "fade-in-out show" : stage > 2 ? "fade-in-out hide" : "fade-in-out";
    case 3: return stage === 3 || stage === 4 ? "fade-in-out show" : stage > 3 ? "fade-in-out hide" : "fade-in-out";
    default: return "fade-in-out";
  }
};

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

  const handleContinue = async () => {
    setLoadingState("question");
    setCurrentTurn(null);
    setAllVoted(false);
    setVotes([]);
    setScenarioData(null);
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
          {scenarioData.image && (
            <div className="scenario-image">
              <img src={scenarioData.image} alt="scenario" className="scenario-img" />
            </div>
          )}
          </div>
          {/* Continue button at bottom */}
          <div className="scenario-footer">
            <Button
              baseButton="btn-primary"
              action={() => {handleContinue()}}
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
            <div className="question-container">
              <h2 className={getFadeClass(1)}>{currentTurn.question}</h2>
            </div>
          </div>
          {/* Right side: voting display */}
          <div className="voting-sidebar">
            <VotingDisplay voters={votes} totalPlayers={totalPlayers} />
          </div>

          {screen === "miniGameWait" && (
            <div className="menu-glass mini-result">
              <h2>🕹️ Tie-Break Mini-Game in Progress...</h2>
              <p>Waiting for players to finish...</p>
            </div>
          )}

          {screen === "miniGameWinner" && winnerInfo && (
            <div className="menu-glass mini-result">
              <h2>🏆 Tie-Break Winner</h2>
              <p>{winnerInfo.winner} wins the tie-break!</p>
              <p>Resuming story...</p>
            </div>
          )}

        </div>
      )}
    </BasePage>
  );
};

export default HostScreen;