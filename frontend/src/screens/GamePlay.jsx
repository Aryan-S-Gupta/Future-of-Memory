import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { getQuestion, submitChoice, } from "../../api/single-player/GameApi";
import { useSession } from "../../SessionContext.jsx";
import background from "../assets/fallback_first_turn.png";
import ExitExperience from "../components/ExitExperience/ExitExperience.jsx";
import Button from "../components/Button/Button.jsx";
import LoadingScreen from "../components/Loading/LoadingScreen.jsx";
import BasePage from "./BasePage.jsx";
import { useBgm } from "../audio/AudioProvider.jsx"; // <-- use bgm state/controls
import { useMemo, useRef } from "react";
import "../styles/GamePlay.css";
import { getFunFacts } from "../../api/single-player/GameApi.js";
import { useNavigate } from "react-router-dom";


/**
 * GamePlay component
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
  const [turn, setTurn] = useState(-1)
  const [loadingFacts, setLoadingFacts] = useState([]);
  const [option_id, setOptionId] = useState(null);
  const [isReady, setIsReady] = useState(false);
  const [loadingState, setLoadingState] = useState("none")
  const [scenarioData, setScenarioData] = useState({
    scenario:
    "The year is 2035, and neurotechnology now makes memory manipulation precise and reliable. " +
    "Once experimental, memory editing, enhancement, and storage are mainstream, forcing governments " +
    "to confront choices that could redefine humanity. Nations clash over freedom versus regulation, while corporations drive new concerns around privacy," +
    " ownership, and the commercialization of consciousness.",
    image: background // no image for the first one
  });

  const navigate = useNavigate();

  // --- Tie narration to BGM ---
  const { isPlaying, volume, setVolume } = useBgm();

  // --- Question Query ---
  // Fetches the question whenever we are on the "question" screen.
  // Fetches the scenario whenever we are on the "scenario" screen.
  const {
    data: questionData
  } = useQuery ({
    queryKey: ["question", sessionId, turn, year], 
    queryFn: async() => {
        console.log(year);
        console.log("queryFn running for", year);
        const result = await getQuestion(sessionId, turn , year);
        if (!result ) {
          setScreen("loading");
          setLoadingState("question");
          await fetchFunFacts();
          console.log("loading at the moment");
          return null;
        } else {
          setCurrentTurn(result);
          setTurn(result.turn_id);
          setScreen("question");
          setLoadingState("none")
          console.log("recieved question data: " + result);
          setScenarioData(null);
          return result;
        }
    }, enabled: loadingState == "question", 
    refetchInterval: 3000,
    refetchIntervalInBackground: true, 
  })

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

  const speak = (text, onDone) => {
    if (!synthRef.current || !text) {
      if (typeof onDone === "function") onDone();
      return;
    }
    // Cancel any previous narration
    cancelTTS();

    // Only narrate if BGM is playing (toolbar controls this)
    if (!isPlaying) {
      if (typeof onDone === "function") onDone();
      return;
    }

    // Lower BGM volume temporarily (minimal approach)
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
    utter.voice = picked;

    utter.rate = 0.7;
    utter.pitch = 1.0;
    utter.volume = 1;

    const restore = () => {
      if (prevVolRef.current !== null) {
        setVolume(prevVolRef.current);
        prevVolRef.current = null;
      }
      if (typeof onDone === "function") onDone();
    };

    utter.onend = restore;
    utter.onerror = restore;

    try {
      synthRef.current.speak(utter);
    } catch {
      restore();
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
  // useEffect(() => {
  //   if (screen === "question" && questionReadout) {
  //     speak(questionReadout);
  //   }
  //   return () => cancelTTS();
  //   // eslint-disable-next-line react-hooks/exhaustive-deps
  // }, [screen, questionReadout, isPlaying]);

  // --- Staged reveal ---
  // 0 = nothing, 1 = question, 2 = option1, 3 = option2, 4 = final all
  const [stage, setStage] = useState(0);
  const fadeDuration = 1000; //
  useEffect(() => {
    if (screen !== "question" || !currentTurn) return;

    let cleared = false;
    let t1, t2, t3;

    const fallback = () => {
      setStage(1); // show question
      t1 = setTimeout(() => setStage(2), 12000 - fadeDuration);
      t2 = setTimeout(() => setStage(3), 18000 - fadeDuration);
      t3 = setTimeout(() => setStage(4), 24000 - fadeDuration);
    };

    const optA = currentTurn?.options?.[0]?.option_text;
    const optB = currentTurn?.options?.[1]?.option_text;

    // If no TTS or not playing, just run fallback timers
    if (!synthRef.current || !isPlaying) {
      fallback();
      return () => {
        cleared = true;
        clearTimeout(t1); clearTimeout(t2); clearTimeout(t3);
        cancelTTS();
      };
    }

    // TTS-driven chain
    setStage(1);
    speak(currentTurn.question, () => {
      if (cleared) return;
      setStage(2);
      if (optA) {
        speak(optA, () => {
          if (cleared) return;
          setStage(3);
          if (optB) {
            speak(optB, () => {
              if (cleared) return;
              setStage(4);
            });
          } else {
            setStage(4);
          }
        });
      } else {
        // No A? Jump forward.
        setStage(3);
        if (optB) {
          speak(optB, () => {
            if (cleared) return;
            setStage(4);
          });
        } else {
          setStage(4);
        }
      }
    });

    return () => {
      cleared = true;
      clearTimeout(t1); clearTimeout(t2); clearTimeout(t3);
      cancelTTS();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [screen, currentTurn, isPlaying]);


  // Map button stage
  const getButtonStageClass = (idx) => {
    if (stage === 4) return "show";
    if (stage === idx + 2) return "show";
    if (stage > idx + 2) return "hide";
    return "";
  };

  // handle choice click
  const handleChoice = async (option_id) => {
    if (!currentTurn) return;
    cancelTTS();
    setScreen("loading");
    setLoadingState("scenario")
    setOptionId(option_id);
    console.log("handleChoice called with option_id:", option_id);
    await fetchFunFacts();


  };

  const {
    data: out,
    isLoading: isTurnLoading,
    error: turnError,
    status: turnStatus,
  } = useQuery({
    queryKey: ["scenario", currentTurn, sessionId, year, option_id],
    queryFn: async () => {
      console.log("submitting option", option_id);
      const out = await submitChoice(sessionId, currentTurn.turn_id, year, option_id);

      if (!out.scenario || !out.scenario.text || !out.image?.url) {
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
      setScreen("scenario");
      console.log("Submit choice response:", mapped);
      setScenarioData(mapped);
      setYear(year + 1);
      return out;
    },
    enabled: screen !== "question" && currentTurn != null && !scenarioData,
    refetchInterval: 3000,
    refetchIntervalInBackground: true,
    onError: (err) => {
      console.error("onError:", err);
    }
  });
  const questionClass =
    stage === 1 || stage === 4 ? "fade-in-out show" :
      stage > 1 ? "fade-in-out hide" : "fade-in-out";

  const optionAClass =
    stage === 2 || stage === 4 ? "choice-btn fade-in-out show" :
      stage > 2 ? "choice-btn fade-in-out hide" : "choice-btn fade-in-out";

  const optionBClass =
    stage === 3 || stage === 4 ? "choice-btn fade-in-out show" :
      stage > 3 ? "choice-btn fade-in-out hide" : "choice-btn fade-in-out";



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
    if (year >= 2035 + 50) {
      navigate(`/gallery/${sessionId}`);
    }
  }, [year, navigate, sessionId]);

  return (
    <BasePage>
      <ExitExperience code="-1" player="single-player" />
      {screen === "loading" && (
        <LoadingScreen
          isReady={isReady}
          funFacts={loadingFacts}
          onContinue={() => {
            setScreen({loadingState});
          }}
        />
      )}

      {screen === "scenario" && scenarioData && (
        <div className="scenario-screen">
          {/* Image in middle */}

          {/* Scenario text at top */}
          <div className="text-container menu-glass">
            {scenarioData.image && (
              <div className="scenario-image">
                <img src={scenarioData.image} alt="scenario" className="scenario-img" />
              </div>
            )}
            <h2 className="fade-in">{scenarioData.scenario}</h2>

          </div>
          <div className="scenario-footer">
            <Button
              baseButton="btn-primary"
              action={() => {
                setScreen("loading");
                setLoadingState("question");
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
        <div className="menu-glass  question-screen-container">
          <div className="question-container">
            <h2 className={questionClass}>
              {currentTurn.question}
            </h2>
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
        </div>
      )}

    </BasePage>
  );
};

export default GamePlay;