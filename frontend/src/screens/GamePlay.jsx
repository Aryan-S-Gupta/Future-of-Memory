import { useState, useEffect } from "react";
import { getQuestion } from "../../api/questionApi";
import { getScenario } from "../../api/scenarioApi";
import { submitChoice } from "../../api/answerApi";
import Button from "../components/Button/Button";
import { useNavigate } from "react-router-dom";

const GamePlay = () => {
  const [year, setYear] = useState(2035);
  // "scenario" or "question" screen - by default it is always set to scenario 
  const [screen, setScreen] = useState("scenario");
  const [scenario, setScenario] = useState("");
  const [question, setQuestion] = useState("");
  const [choices, setChoices] = useState([]);
  const [outcome, setOutcome] = useState("");
  const [outcomeMap, setOutcomeMap] = useState({});
  

  // Load scenario whenever year changes and user has completed answering questions
  useEffect(() => {
    const loadScenario = async () => {
      const s = await getScenario(year);
      setScenario(s.scenario);
    };
    loadScenario();
  }, [year]);

  // helper function to change state to questions 
  const goToQuestion = async () => {
    const q = await getQuestion(year);
    // need to add logic for questions screen here 
    setScreen("question");
  };

  const navigate = useNavigate();

  return (
    <div className="screen">
      <Button baseButton="btn-back" action={() => navigate("/")} title="Back" />
      {/* Scenario screen UI*/}
      {screen === "scenario" && (
        <div className="text-container">
          <h3>{scenario}</h3>
          <Button baseButton="btn-primary" action={goToQuestion} title="Continue"/>
        </div>
      )}
    </div>
  );
};

export default GamePlay;
