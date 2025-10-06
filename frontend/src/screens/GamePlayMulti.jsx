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

const GamePlayMulti = () => {
  const navigate = useNavigate();
  const { roomCode } = useParams(); 
  const [searchParams] = useSearchParams();
  const playerName = searchParams.get("playerName");
  const { sessionId } = useSession(); // <-- get session from context
  const [year, setYear] = useState(2035);
  const [screen, setScreen] = useState("scenario"); // "scenario" or "question"
  const [currentTurn, setCurrentTurn] = useState(null);
    const [loadingFacts, setLoadingFacts] = useState([]);
    const [isReady, setIsReady] = useState(false);
    const [option_id, setOptionId] = useState(null);
  const [turn, setTurn] = useState(-1);
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
  data: questionData,
  isLoading: isQuestionLoading,
  error: questionError,
  status,
  } = useQuery({
    queryKey: ["question", roomCode, sessionId, turn],
    queryFn: async () => {
      console.log("queryFn running for", sessionId);
      const result = await getQuestion(roomCode, sessionId, turn);
      if (!result.success) {
        if (!result.room_exists) {
          setRoomDestroyed(true);
          console.log("the room does not exists")
          setScreen("destroyed")
          // handle room doesnt exist
        }
      }
      console.log("currentTurn after getQuestion:", currentTurn);
      console.log("queryFn result:", result);
      setCurrentTurn(result);
      setTurn(result.data.turn_id);
      return result;
    },
    enabled: screen === "question",
    onError: (err) => {
      console.error("onError:", err);
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

    // --- Staged reveal for multiplayer ---
  // 0 = nothing, 1 = question, 2 = option1, 3 = option2, 4 = final all
  const [stage, setStage] = useState(0);
  const fadeDuration = 2000;

  useEffect(() => {
    if (screen === "question" && currentTurn) {
      setStage(1); // show question
      speak(currentTurn.question);

      const timer1 = setTimeout(() => {
        setStage(2);
        speak(currentTurn.options[0].option_text);
      }, 12000 - fadeDuration);

      const timer2 = setTimeout(() => {
        setStage(3);
        speak(currentTurn.options[1].option_text);
      }, 17000 - fadeDuration);

      const timer3 = setTimeout(() => {
        setStage(4); // show all together, no TTS
      }, 22000 - fadeDuration);

      return () => {
        clearTimeout(timer1);
        clearTimeout(timer2);
        clearTimeout(timer3);
        cancelTTS();
      };
    }
  }, [screen, currentTurn]);

  const questionClass =
    stage === 1 || stage === 4 ? "fade-in-out show" :
      stage > 1 ? "fade-in-out hide" : "fade-in-out";

  const optionAClass =
    stage === 2 || stage === 4 ? "choice-btn fade-in-out show" :
      stage > 2 ? "choice-btn fade-in-out hide" : "choice-btn fade-in-out";

  const optionBClass =
    stage === 3 || stage === 4 ? "choice-btn fade-in-out show" :
      stage > 3 ? "choice-btn fade-in-out hide" : "choice-btn fade-in-out";
  /**
   * Handles a player's choice when answering a question.
   *
   * @param {string} answer - The key of the chosen option.
   */

  // handle choice click
  const handleChoice = async (option_id) => {
    if (!currentTurn) return;
    cancelTTS(); 
    setScreen("loading");
    setOptionId(option_id);
    setIsReady(false);
    await fetchFunFacts();

    
  };

const {
  data: out,
  isLoading: isTurnLoading,
  error: turnError,
  status: turnStatus,
  } = useQuery({
    queryKey: ["scenario", playerName, roomCode, currentTurn, sessionId, roomCode, option_id, year],
    queryFn: async () => {
      console.log("submitting option", sessionId);
      const out = await submitChoice(playerName, roomCode, sessionId,currentTurn.turn_id, year, option_id);
      if (!out.success) {
        if (!out.room_exists) {
          setRoomDestroyed(true); 
          setScreen("destroyed")
          // handle room doesnt exist
        }
      }
      console.log("the data is", out.data );

      if (!out.scenario || !out.scenario.text) {
        console.log("Scenario/image not ready yet...");
        return null;
    } else if (out.scenario.text === scenarioData?.scenario) {
      console.log("Scenario/image unchanged, waiting...");
      return null;
    }
      const mapped = {
        scenario: out.scenario.text,
        image: out.image.url
      };
      console.log("Submit choice response:", mapped);
      setIsReady(true);
      setScenarioData(mapped);
      // setScreen("scenario");
      setYear(year + 1);
    },
    enabled: screen !== "question" && currentTurn != null && screen !== "destroyed",
    onError: (err) => {
      console.error("onError:", err);
    }
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
          setScreen("scenario");
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
                console.log("Session ID:", sessionId);
              }}
              title="Continue"
            />
          </div>
        </div>
      )}
      {/** Question Screen*/}
      {screen === "question" && currentTurn && (
        <div>
          <div className="question-container">
            <h2 className={questionClass}>{currentTurn.question}</h2>
          </div>
          <div className="choice-container">
            <Button
              baseButton={optionAClass}
              action={() => handleChoice(currentTurn.options[0].option_id)}
              title={`${currentTurn.options[0].label}. ${currentTurn.options[0].option_text}`}
            />
            <Button
              baseButton={optionBClass}
              action={() => handleChoice(currentTurn.options[1].option_id)}
              title={`${currentTurn.options[1].label}. ${currentTurn.options[1].option_text}`}
            />
          </div>
        </div>
      )}

    </BasePage>
  );
};

export default GamePlayMulti;