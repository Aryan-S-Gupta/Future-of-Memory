import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getQuestion, submitChoice } from "../../api/single-player/GameApi";
import Button from "../components/Button/Button";
import { useNavigate } from "react-router-dom";
import { useSession } from "../../SessionContext";
import "./GamePlay.css";
import { useMutation } from "@tanstack/react-query";

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
    "The year is 2035. Breakthrough advances in neurotechnology have made human memory" +
    "manipulation not just possible, but precise and reliable. Memory editing, enhancement," +
    " and storage technologies have matured from experimental procedures to commercially " +
    "viable solutions Global governments now face unprecedented policy decisions that will " + 
    "fundamentally reshape human society. Memory modification technologies can eliminate " +
    "traumatic experiences, enhance learning capabilities, allow perfect recall of any information," +
    " and even enable memory sharing between individuals. These capabilities present both extraordinary "+
    " opportunities and profound risks. The international community stands at a crossroads. Some nations advocate for unrestricted access to memory technologies, viewing them as the next step in human evolution. Others call for strict regulation, warning of potential misuse and the erosion of human authenticity. Meanwhile, private corporations have developed sophisticated memory storage systems, creating new questions about data ownership, privacy, and commercial exploitation of human consciousness.",
  image: "../assets/background.jpg", // no image for the first one
});

  const navigate = useNavigate();

  // --- Scenario Query ---
  // Fetches the scenario whenever we are on the "scenario" screen.
  const {
    data: questionData,
    isLoading: isQuestionLoading,
    error: questionError,
  } = useQuery({
    queryKey: ["question", sessionId],
    queryFn: () => getQuestion(sessionId),
    enabled: screen === "question" && !!sessionId,
    refetchInterval: 2000,
    onSuccess: (res) => {
      console.log("Question response:", res);

      setCurrentTurn(res.data.data); // maybe should be just res instead of res.data
    }
  });

  // --- Submit Choice Mutation ---
  const choiceMutation = useMutation({
    mutationFn: ({ turn_id, year, option_id }) =>
      submitChoice(sessionId, turn_id, year, option_id),
    onSuccess: (res) => {
      console.log("Submit choice response:", res);
      setScenarioData(res); // { scenario, image, ... }
      setScreen("scenario");
    },
  });

  // handle choice click
  const handleChoice = (option_id) => {
    if (!currentTurn) return;
    choiceMutation.mutate({
      turn_id: currentTurn.turn_id,
      year: currentTurn.year,
      option_id,
    });
  };

  // --- UI Loading/Error States ---
  if (isQuestionLoading || !questionData) return <p>Waiting for question to be generated...</p>;
  if (isQuestionLoading && screen === "question") return <p>Loading question...</p>;
  if (questionError) return <p>Error loading question</p>;
  if (choiceMutation.isLoading) return <p>Submitting choice...</p>;


  return (
    <div className="screen">
      <Button baseButton="btn-back" action={() => navigate("/")} title="Back" />

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
            console.log("Fetching question for session:");
            setScreen("question");
            console.log("Fetching question for session:");

            query.refetch(); // force query to run when entering question screen
            console.log("Fetching question for session:");
          }}
          title="Continue"
        />
        </div>
      )}

      {/* Question Screen */}
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
                title={`${opt.label}: ${opt.option_text}`}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default GamePlay;