import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { getQuestion } from "../../api/questionApi";
import { getScenario } from "../../api/scenarioApi";
import { submitChoice } from "../../api/answerApi";
import Button from "../components/Button/Button";
import { useNavigate } from "react-router-dom";

const GamePlay = () => {
  const [year, setYear] = useState(2035);
  const [screen, setScreen] = useState("scenario"); // "scenario" or "question"
  const navigate = useNavigate();

  // Fetch scenarios everytim the screen changes to scenario
  const {
    data: scenarioData,
    isLoading: isScenarioLoading,
    error: scenarioError,
  } = useQuery({
    queryKey: ["scenario", year],
    queryFn: () => getScenario(year),
    enabled: screen === "scenario", 
  });

  // Fetches questiosn everytime the scren chnges to questions screen
  const {
    data: questionData,
    isLoading: isQuestionLoading,
    error: questionError,
  } = useQuery({
    queryKey: ["question", year],
    queryFn: () => getQuestion(year),
    enabled: screen === "question", // only fetch when we are on question screen
  });

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
          <h3>{scenarioData.scenario}</h3>
          <Button baseButton="btn-primary" action={() => setScreen("question")} title="Continue"/>
        </div>
      )}
    </div>
  );
};

export default GamePlay;
