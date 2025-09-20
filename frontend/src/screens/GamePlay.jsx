// frontend/src/pages/GamePlay.jsx
import React, { useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getQuestion } from "../../api/questionApi";
import { getScenario } from "../../api/scenarioApi";
import { submitChoice } from "../../api/answerApi";
import Button from "../components/Button/Button";
import { useNavigate } from "react-router-dom";
import "../styles/GamePlay.css";
import BasePage from "./BasePage.jsx";
import { useBgm } from "../audio/AudioProvider.jsx"; // <-- use bgm state/controls

/**
 * GamePlay component
 *
 * This screen drives the main gameplay loop. It alternates between:
 * - Displaying a **scenario** for the given year.
 * - Displaying a **decision-making question** with multiple choices.
 *
 * Features:
 * - Uses React Query to fetch scenario/question data from backend APIs.
 * - Tracks the current year (`year`) and current screen (`screen`).
 * - Handles user choices and progresses the game timeline forward.
 * - Provides navigation back to the home screen.
 *
 * @component
 * @returns {JSX.Element} The interactive gameplay screen with scenario/question flow.
 */
const GamePlay = () => {
  const [year, setYear] = useState(2035);
  const [screen, setScreen] = useState("scenario"); // "scenario" or "question"
  const navigate = useNavigate();

  // --- Tie narration to BGM ---
  const { isPlaying, volume, setVolume } = useBgm();

  // --- Scenario Query ---
  // Fetches the scenario whenever we are on the "scenario" screen.
  const {
    data: scenarioData,
    isLoading: isScenarioLoading,
    error: scenarioError,
  } = useQuery({
    queryKey: ["scenario", year],
    queryFn: () => getScenario(year),
    enabled: screen === "scenario",
  });

  // --- Question Query ---
  // Fetches the question whenever we are on the "question" screen.
  const {
    data: questionData,
    isLoading: isQuestionLoading,
    error: questionError,
  } = useQuery({
    queryKey: ["question", year],
    queryFn: () => getQuestion(year),
    enabled: screen === "question", // only fetch when we are on question screen
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
    utter.rate = 1;
    utter.pitch = 1;
    // Let TTS be clearly audible regardless; we already lowered BGM
    utter.volume = 1;

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
  const handleChoice = async (answer) => {
    try {
      cancelTTS(); // stop narration immediately
      submitChoice(year, answer);
      setScreen("scenario");
      setYear((year) => year + 1);
    } catch (error) {
      console.error("Error submitting choice:", error);
    }
  }

  // --- UI Loading/Error States ---
  if (isScenarioLoading && screen === "scenario") return <p>Loading scenario...</p>;
  if (isQuestionLoading && screen === "question") return <p>Loading question...</p>;
  if (scenarioError) return <p>Error loading scenario</p>;
  if (questionError) return <p>Error loading question</p>;

  return (
    <BasePage>

      <Button baseButton="btn-back" action={() => { cancelTTS(); navigate("/"); }} title="Back" />

      {/* Scenario screen */}
      {screen === "scenario" && scenarioData && (
        <div className="text-container">
          <h2 className="fade-in">{scenarioData.scenario}</h2>
          <Button baseButton="btn-primary" action={() => setScreen("question")} title="Continue" />
        </div>
      )}
      {/** Question Screen*/}
      {screen === "question" && questionData && (
        <div>
          <div className="question-container">
            <h2 className="fade-in">{questionData.question}</h2>
          </div>
          <div className="choice-container">
            {/*Displays the questions and the choices */}
            {Object.entries(questionData.options).map(([key, value]) => (
              <Button
                baseButton="choice-btn choice-fade-in"
                key={key}
                action={() => handleChoice(key)}
                title={value} />
            ))}
          </div>
        </div>
      )}

    </BasePage>
  );
};

export default GamePlay;
