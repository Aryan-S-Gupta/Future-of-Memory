import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { getQuestion, submitChoice } from "../../api/multiplayer/GameFlowApi.js";
import { getRoomState } from "../../api/multiplayer/RoomManagementApi.js";
import Button from "../components/Button/Button.jsx";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import "../styles/GamePlay.css";
import { useSession } from "../../SessionContext.jsx";
import background from "../assets/background.jpg";
import { getFunFacts } from "../../api/single-player/GameApi.js";
import ExitExperience from "../components/ExitExperience/ExitExperience.jsx";
import BasePage from "./BasePage.jsx";
import { useBgm } from "../audio/AudioProvider.jsx"; // <-- use bgm state/controls
import { useMemo, useRef } from "react";
import LoadingScreen from "../components/Loading/LoadingScreen.jsx";
import RoomDestroyedPopup from "../components/RoomDestroy/RoomDestroyedDisplay.jsx";
import VotingDisplay from "../components/Voting Display/VotingDisplay.jsx";
import { getVotingInfo} from "../../api/multiplayer/GameFlowApi";


const GamePlayMulti = () => {
  const navigate = useNavigate()
  const { roomCode } = useParams(); 
  const [searchParams] = useSearchParams();
  const playerName = searchParams.get("playerName");
  const prevQuestionRef = useRef(null);
  const { sessionId } = useSession(); // <-- get session from context
  const [year, setYear] = useState(2035);
  const [screen, setScreen] = useState("scenario"); // "scenario" or "question"
  const [currentTurn, setCurrentTurn] = useState(null);
    const [loadingFacts, setLoadingFacts] = useState([]);
    const [isReady, setIsReady] = useState(false);
    const [option_id, setOptionId] = useState(null);
  const [turn, setTurn] = useState(-1);
  const [showVotes, setShowVotes] = useState(false)
  const [votes, setVotes] = useState([]);
  const [totalPlayers, setTotalPlayers] = useState(1);
  const [fetchVoteData, setFetchVoteData] = useState(true);
  // --- Staged reveal for multiplayer ---
  // 0 = nothing, 1 = question, 2 = option1, 3 = option2, 4 = final all
  const [stage, setStage] = useState(0);
  
  const [hasAnimated, setHasAnimated] = useState(false); 
  const fadeDuration = 2000;

  const [loadingState, setLoadingState] = useState("question")
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
// Fetches the scenario whenever we are on the "scenario" screen.

 

const {
  data: questionData
  } = useQuery({
    queryKey: ["question", roomCode, sessionId, turn],
    queryFn: async () => {
      console.log("queryFn running for", sessionId);
      setIsReady(false);
      console.log(year);
      const result = await getQuestion(sessionId, roomCode, turn, year);
      console.log("the result was " + result)
      if (!result) {
        setScreen("loading");
        setLoadingState("question");           
        await fetchFunFacts();
        console.log("the loaidng state updated")
        return null;
      } else {
        setScreen("question");
        setShowVotes(true);
        console.log("currentTurn after getQuestion:", currentTurn);
        console.log("queryFn result:", result);
        setCurrentTurn(result);
        console.log("show votes turned on line 75")
        setTurn(result.turn_id);
        //setFetchQuestion(false);

        setLoadingState("scenario")

        console.log("show votes turned on 77");
        console.log("show votes turned on")
        return result;
 
      }

    },
    enabled: screen !== "scenario" && loadingState != "scenario",
    onError: (err) => {
      console.log("onError:", err);

    }, refetchInterval: (data) => {
          if (data != null) {
            return false;
          } else {
            return 3000;
          }
    }
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





const { data: votingData } = useQuery({
  queryKey: ["votingStatus", roomCode, currentTurn?.turn_id],
  queryFn: async () => {
    if (!currentTurn) {
      console.log("[VotingQuery] Skipped fetch — no currentTurn yet.");
      return null;
    }

    console.log(
      `[VotingQuery] Fetching voting info for room=${roomCode}, turn=${currentTurn.turn_id}...`
    );

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
    setVotes(mappedVotes);
    setTotalPlayers(data.total_players);

    const votesCount = data.num_responses;
    const totalCount = data.total_players;
    const allVoted = votesCount >= totalCount;

    console.log(
      `[VotingQuery] Vote Progress: ${votesCount}/${totalCount} | All voted? ${allVoted}`
    );

    if (allVoted) {
      console.log("All players voted!");
      setScreen("loading")
      setLoadingState("scenario")
      await fetchFunFacts();
      if (!scenarioData || !scenarioData.scenario) {
        console.log("Scenario not ready → go to loading screen");
        setScreen("loading");
        setLoadingState("scenario");
        await fetchFunFacts();
      } else {
        console.log("Scenario ready → show scenario");
        setScreen("scenario");
      }
      setVotes([]);
      setShowVotes(false);
    }
      },
      enabled: screen === "question" && currentTurn != null && loadingState != "question" && showVotes === false,
      refetchInterval: currentTurn ? 3000 : false, // poll every 3s
        onError: (err) => {
        console.error("[VotingQuery] onError triggered:", err);
  }});

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


  /**
   * Handles a player's choice when answering a question.
   *
   * @param {string} answer - The key of the chosen option.
   */

  // handle choice click
  const handleChoice = async (option_id) => {
    if (!currentTurn) return;
    cancelTTS(); 
    setOptionId(option_id);
    setLoadingState("scenario")
  }

// make a var using states, shpw votes, when the screen is questions screen then start calling the voting again and again
// once the votes == total player , set screen == loading 
// u want to have another one of these API calls with refetch so that it keeps rendered the voting display and once all the players have voted set screen == loaidng 
// remove the set loading from submit choice and move it to loaidng screen
  const {
    data: out,
    isLoading: isTurnLoading,
    error: turnError,
    status: turnStatus,
    } = useQuery({
      queryKey: ["scenario", playerName, roomCode, currentTurn, sessionId, roomCode, option_id, year],
      queryFn: async () => {
        console.log("submitting option", sessionId);
        if (!currentTurn || !option_id) return;
        const out = await submitChoice(playerName, roomCode, sessionId,currentTurn.turn_id, year, option_id);
        if (!out || !out.scenario || !out.scenario.text) {
          if (!out.room_exists) {
            setRoomDestroyed(true); 
            setScreen("destroyed")
            // handle room doesnt exist
          }
          console.log("dont have scenario yet");
          setScreen("loading");
          setLoadingState("scenario");
      }
      console.log("the data is", out );

    // if (out.scenario.text === scenarioData?.scenario) {
    //   setIsReady(False)
    //   setScreen("loading");
    //   setLoadingState("scenario");
    //   console.log("Scenario/image u nchanged, waiting...");
    //   return null;
    // }
      const mapped = {
        scenario: out.scenario.text,
        image: out.image.url
      };
      console.log("Submit choice response:", mapped);
      setIsReady(true);
      setScreen("scenario")
      setScenarioData(mapped);
      setYear(year + 1);
    },
    enabled: currentTurn != null &&  option_id != null && screen !== "destroyed" && loadingState !== "question",
    onError: (err) => {
      console.log("onError:", err);
    }, 
    refetchInterval: 3000
});

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
      <ExitExperience code={roomCode} player={playerName}/>
      {screen == "destroyed" && (
        <RoomDestroyedPopup/>
      )}
            {screen === "loading" && (
      <LoadingScreen
        isReady={isReady}
        funFacts={loadingFacts}
        onContinue={() => {
          setShowVotes(false);
          setVotes([]);
          setScreen({loadingState});
        }}  
      />
    )}
      {screen === "scenario" && scenarioData && (
        <div className="scenario-screen">
              {/* Image in middle */}
          {scenarioData.image && ( 
            <div className="scenario-image">
              <img src={scenarioData.image} alt="scenario" className="scenario-img" />
            </div>
          )}
          {/* Scenario text at top */}
          <div className="text-container">
            <h2 className="fade-in">{scenarioData.scenario}</h2>
          </div>



          {/* Continue button at bottom */}
          <div className="scenario-footer">
            <Button
              baseButton="btn-primary"
              action={() => {
                setScreen("question");
                setLoadingState("question");
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
          <div className="question-main">
            <div className="question-container">
              <h2 className={getFadeClass(1)}>{currentTurn.question}</h2>
            </div>
            <div className="choice-container">
              <Button
                baseButton={getFadeClass(2) + " choice-btn"}
                action={() => handleChoice(currentTurn.options[0].option_id)}
                title={`${currentTurn.options[0].label}. ${currentTurn.options[0].option_text}`}
              />
              <Button
                baseButton={getFadeClass(3) + " choice-btn"}
                action={() => handleChoice(currentTurn.options[1].option_id)}
                title={`${currentTurn.options[1].label}. ${currentTurn.options[1].option_text}`}
              />
            </div>
          </div>
          
          <div className="voting-sidebar">
            <VotingDisplay voters={votes} totalPlayers={totalPlayers} />
          </div>
        </div>
      )}

    </BasePage>
  );
};

export default GamePlayMulti;