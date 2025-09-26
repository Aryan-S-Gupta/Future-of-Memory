import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { getScenario, getQuestion, submitChoice } from "../../api/multiplayer/GameFlowApi.js";
import { getRoomState } from "../../api/multiplayer/RoomManagementApi.js";
import Button from "../components/Button/Button.jsx";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import "../styles/GamePlay.css";

const GamePlayMulti = () => {
  const navigate = useNavigate();
  const { roomCode } = useParams(); 
  const [searchParams] = useSearchParams();
  const playerName = searchParams.get("playerName");

  const [screen, setScreen] = useState("scenario"); // "scenario" or "question"
  const [year, setYear] = useState(2035);
  const [otherPlayersChoices, setOtherPlayersChoices] = useState({});
  const [outcome, setOutcome] = useState(null);
  const [waiting, setWaiting] = useState(false);

  // Fetch the current scenario
  const { data: scenarioData } = useQuery({
    queryKey: ["scenario", roomCode, year],
    queryFn: () => getScenario(roomCode, year),
    enabled: screen === "scenario",
  });

  // Fetch the current question
  const { data: questionData } = useQuery({
    queryKey: ["question", roomCode, year],
    queryFn: () => getQuestion(roomCode, year),
    enabled: screen === "question",
  });

  // Polling room state to get other players' choices
  useEffect(() => {
    if (screen === "question") {
      const interval = setInterval(async () => {
        const state = await getRoomState(roomCode);
        setOtherPlayersChoices(state.playersChoices);
        if (state.allAnswered) {
          setOutcome(state.outcome);
          setWaiting(false);
        }
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [screen, roomCode]);

  const handleChoice = async (choice) => {
    setWaiting(true);
    await submitChoice(roomCode, playerName, year, choice);
  };

  const handleNext = () => {
    setScreen("scenario");
    setYear(year + 1);
    setOtherPlayersChoices({});
  };

  if (!scenarioData || !questionData) return <p>Loading...</p>;

  return (
    <div className="screen">
      <Button baseButton="btn-back" action={() => navigate("/")} title="Back" />

      {screen === "scenario" && (
        <div className="text-container">
          <h2 className="fade-in">{scenarioData.scenario}</h2>
          <Button baseButton="btn-primary" action={() => setScreen("question")} title="Continue"/>
        </div>
      )}

      {screen === "question" && (
        <div>
          <div className="question-container">
            <h2 className="fade-in">{questionData.question}</h2>
          </div>
          <div className="choice-container">
            {Object.entries(questionData.options).map(([key, value]) => (
              <Button
                baseButton="choice-btn choice-fade-in"
                key={key}
                action={() => handleChoice(key)}
                title={value}
                disabled={waiting}
              />
            ))}
          </div>

          {waiting && <p>Waiting for other players...</p>}

          {outcome && (
            <div>
              <p>Outcome: {questionData.options[outcome]}</p>
              <Button baseButton="btn-next" action={handleNext} title="Next Scenario" />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default GamePlayMulti;
