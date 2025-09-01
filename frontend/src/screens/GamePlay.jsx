import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { getQuestion } from "../../api/questionApi";
import { getScenario } from "../../api/scenarioApi";
import { submitChoice } from "../../api/answerApi";
import Button from "../components/Button/Button";
import { useNavigate } from "react-router-dom";
import "./GamePlay.css";

const GamePlay = () => {
  const [year, setYear] = useState(2035);
  const [screen, setScreen] = useState("scenario"); // "scenario" or "question"
  const navigate = useNavigate();

  // Fetch scenarios everytime the screen changes to scenario
  const {
    data: scenarioData,
    isLoading: isScenarioLoading,
    error: scenarioError,
  } = useQuery({
    queryKey: ["scenario", year],
    queryFn: () => getScenario(year),
    enabled: screen === "scenario", 
  });

  // Fetches questions everytime the scren chnges to questions
  const {
    data: questionData,
    isLoading: isQuestionLoading,
    error: questionError,
  } = useQuery({
    queryKey: ["question", year],
    queryFn: () => getQuestion(year),
    enabled: screen === "question", // only fetch when we are on question screen
  });

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
          <h2>{scenarioData.scenario}</h2>
          <Button baseButton="btn-primary" action={() => setScreen("question")} title="Continue"/>
        </div>
      )}
      {/** Question Screen*/}
      {screen === "question" && questionData && (
        <div>
          <div className="question-container">
          <h2>{questionData.question}</h2>
        </div>
        <div className="choice-container">
          {/*Displays the questions and the choices */}
            {Object.entries(questionData.options).map(([key, value]) => (
              <Button
                baseButton="choice-btn"
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
