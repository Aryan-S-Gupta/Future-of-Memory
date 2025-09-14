import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { getQuestion } from "../../api/questionApi";
import { getScenario } from "../../api/scenarioApi";
import { submitChoice } from "../../api/answerApi";
import Button from "../components/Button/Button";
import { useNavigate } from "react-router-dom";
import "../styles/GamePlay.css";

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
  
  /**
   * Handles a player's choice when answering a question.
   *
   * @param {string} answer - The key of the chosen option.
   */
  const handleChoice = async (answer) => {
    try {
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
    <div className="screen">
    

      <Button baseButton="btn-back" action={() => navigate("/")} title="Back" />

      {/* Scenario screen */}
      {screen === "scenario" && scenarioData && (
        <div className="text-container">
          <h2 className="fade-in">{scenarioData.scenario}</h2>
          <Button baseButton="btn-primary" action={() => setScreen("question")} title="Continue"/>
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

    </div>
  );
};

export default GamePlay;
