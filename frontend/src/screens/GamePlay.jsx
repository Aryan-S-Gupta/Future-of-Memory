import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { getQuestion, submitChoice,  } from "../../api/single-player/GameApi";
import Button from "../components/Button/Button";
import { useNavigate } from "react-router-dom";
import { useSession } from "../../SessionContext.jsx";
import background from "../assets/background.jpg";
import ExitExperience from "../components/ExitExperience/ExitExperience.jsx";
import LoadingScreen from "../components/Loading/LoadingScreen.jsx";
import BasePage from "./BasePage.jsx";
import { useBgm } from "../audio/AudioProvider.jsx"; // <-- use bgm state/controls
import { useMemo, useRef } from "react";
import { useMutation } from "@tanstack/react-query";
import "../styles/GamePlay.css";
import { getFunFacts } from "../../api/single-player/GameApi.js";



/**
 * GamePlay component
 *
 * This screen drives the main gameplay loop. It alternates between:
 * - Displaying a scenario for the given year.
 * - Displaying a decision-making question** with multiple choices.
 *
 * Features:
 * - Uses React Query to fetch scenario/question data from backend APIs.
 * - Tracks the current year ('year') and current screen ('screen').
 * - Handles user choices and progresses the game timeline forward.
 * - Provides navigation back to the home screen.
 *
 * @component
 * @returns {JSX.Element} The interactive gameplay screen with scenario/question flow.
 */
const GamePlay = () => {
  const { sessionId } = useSession(); // <-- get session from context
  const [year, setYear] = useState(2035);
  const [screen, setScreen] = useState("scenario"); // "scenario" or "question"
  const [currentTurn, setCurrentTurn] = useState(null);
  const [isLoadingScenario, setIsLoadingScenario] = useState(false);
  const [loadingFacts, setLoadingFacts] = useState([]);

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
    queryKey: ["question", sessionId],
    queryFn: async () => {
      console.log("queryFn running for", sessionId);
      const result = await getQuestion(sessionId);
      console.log("queryFn result:", result);
      setCurrentTurn(result)
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
      await fetchFunFacts();

    const out = await submitChoice(sessionId, currentTurn.turn_id, year, option_id);

    if (!out.scenario || !out.scenario.text || !out.image?.url) {
      console.log("Scenario/image not ready yet...");
      return;
    }

    setScenarioData({ scenario: out.scenario.text, image: out.image.url });
    setScreen("scenario");
    setYear(year + 1);
  };

  // Fetch fun facts when loading scenario
  const fetchFunFacts = async () => {
    try {
      const facts = await getFunFacts(); // Fetch 3 fun facts
      setLoadingFacts(facts);
    } catch (error) {
        console.error("Error fetching fun facts:", error);
    }
  }
  return (
    <BasePage>
      <ExitExperience/>
      {screen === "loading" && (
      <LoadingScreen
        isReady={scenarioData?.scenario && scenarioData?.image}
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
            <h2 className="fade-in">{currentTurn.question}</h2>
          </div>
          <div className="choice-container">
            {currentTurn.options.map((opt) => (
              <Button
                baseButton="choice-btn choice-fade-in"
                key={opt.option_id}
                action={() => handleChoice(opt.option_id)}
                title={`${opt.label}. ${opt.option_text}`}
              />
            ))}
          </div>
        </div>
      )}

    </BasePage>
  );
};

export default GamePlay;