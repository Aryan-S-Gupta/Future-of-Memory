import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getQuestion, submitChoice } from "../../api/single-player/GameApi";
import Button from "../components/Button/Button";
import { useNavigate } from "react-router-dom";
import { useSession } from "../../SessionContext.jsx";
import "./GamePlay.css";
import { useMutation } from "@tanstack/react-query";
import background from "../assets/background.jpg";


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

  const navigate = useNavigate();

  // --- Scenario Query ---
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


  // handle choice click
  const handleChoice = async (option_id) => {
    if (!currentTurn) return;
    const out = await submitChoice(sessionId, currentTurn.turn_id, year, option_id)
        const mapped = {
        scenario: out.scenario.text,
        image: out.image.url
      };
      if (out.image.status !== "ready" ) {
        console.log("Failed to submit choice:", out.message);
      }
      console.log("Submit choice response:", mapped);
      setScenarioData(mapped);
      setScreen("scenario");
      setYear(year + 1);
      };

  return (
    <div className="screen">
      <Button baseButton="btn-back" action={() => navigate("/")} title="Exit Experience" />

      {/* Scenario Screen */}
      {screen === "scenario" && scenarioData && (
        <div className="text-container">
          <h2 className="fade-in">{scenarioData.scenario}</h2>
          {scenarioData.image && (
            <img src={scenarioData.image} alt="scenario" className="scenario-img" />
          )}
        <Button
          baseButton="btn-primary"
          action={() => {
            setScreen("question");
            console.log("Session ID:", sessionId);

          }}
          title="Continue"
        />
        </div>
      )}
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

    </div>
  );
};

export default GamePlay;