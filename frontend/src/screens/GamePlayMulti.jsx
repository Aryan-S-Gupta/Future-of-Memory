import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { getQuestion, submitChoice } from "../../api/multiplayer/GameFlowApi.js";
import { getRoomState } from "../../api/multiplayer/RoomManagementApi.js";
import Button from "../components/Button/Button.jsx";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import "../styles/GamePlay.css";
import { useSession } from "../../SessionContext.jsx";
import background from "../assets/background.jpg";
import { getFunFacts } from "../../api/single-player/GameApi.js";
import ExitExperience from "../components/ExitExperience/ExitExperience.jsx";
import BasePage from "./BasePage.jsx";
import { useBgm } from "../audio/AudioProvider.jsx"; // <-- use bgm state/controls
import { useMemo, useRef } from "react";
import LoadingScreen from "../components/Loading/LoadingScreen.jsx";
import RoomDestroyedPopup from "../components/RoomDestroy/RoomDestroyedDisplay.jsx";
import VotingDisplay from "../components/Voting Display/VotingDisplay.jsx";
import { getVotingInfo} from "../../api/multiplayer/GameFlowApi";
import MiniGame from "./MiniGame.jsx";
import { submitTiebreakScore } from "../../api/multiplayer/GameFlowApi.js";



const GamePlayMulti = () => {
  const navigate = useNavigate()
  const { roomCode, playerName } = useParams(); 
  const prevQuestionRef = useRef(null);
  const { sessionId } = useSession(); // <-- get session from context
  const [year, setYear] = useState(2035);
  const [screen, setScreen] = useState("scenario"); // "scenario" or "question"
  const [currentTurn, setCurrentTurn] = useState(null);
  const [loadingFacts, setLoadingFacts] = useState([]);
  const [isReady, setIsReady] = useState(false);
  const [option_id, setOptionId] = useState(null);
  const [turn, setTurn] = useState(-1);
  const [showVotes, setShowVotes] = useState(false)
  const [votes, setVotes] = useState([]);
  const [totalPlayers, setTotalPlayers] = useState(1);
  const [miniGameOccurred, setMiniGameOccurred] = useState(false);
  const [winnerInfo, setWinnerInfo] = useState(null);
  const [showWinner, setShowWinner] = useState(false);
  const [played, setPlayed] = useState(false)

  // --- Staged reveal for multiplayer ---
  // 0 = nothing, 1 = question, 2 = option1, 3 = option2, 4 = final all
  const [stage, setStage] = useState(0);
  
  const [hasAnimated, setHasAnimated] = useState(false); 
  const fadeDuration = 2000;
  const [allVoted, setAllVoted] = useState(false);
  const [loadingState, setLoadingState] = useState("none")
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
  const [roomDestroyed, setRoomDestroyed] = useState(false);



  // --- Tie narration to BGM ---
  const { isPlaying, volume, setVolume } = useBgm();


  // --- Question Query ---
  // Fetches the question whenever we are on the "question" screen.
// Fetches the scenario whenever we are on the "scenario" screen.
  const {
    data: questionData
  } = useQuery ({
    queryKey: ["question", roomCode, sessionId, turn, year], 
    queryFn: async() => {
        console.log("queryFn running for", year);
        const result = await getQuestion(sessionId, roomCode, turn , year);
        if (!result ) {
          setScreen("loading");
          setLoadingState("question");
          await fetchFunFacts();
          console("loading at the moment");
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
    refetchInterval: (result) => {
        if (result != null) {
          return false;
        } else {
          3000;
        }
    }, refetchIntervalInBackground: true, 
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


 



  const {data: votingData} = useQuery({
    queryKey: ["votingStatus", roomCode, currentTurn?.turn_id], 
    queryFn: async() => {
        console.log("the current turn is: " + currentTurn)
        console.log(
        `[VotingQuery] Fetching voting info for room=${roomCode}, turn=${currentTurn.turn_id}...`
        );
        if (currentTurn === null) return;
        const res = await getVotingInfo(roomCode, currentTurn.turn_id);
        console.log("[VotingQuery] Raw API response:", res);
        const data = res.data
        console.log("[VotingQuery] Parsed data:", res.data);
        console.log("[VotingQuery] onSuccess triggered. Data:", data);
        if (!data) {
          console.log("[VotingQuery] Data empty, skipping state update.");
          return;
        }
              // Map backend vote dictionary → frontend structure
        const mappedVotes = Object.entries(data.votes).map(([player, option]) => ({
          name: player,
          votedFor: option,
          hasVoted: option !== "Pending",
        }));
        console.log(mappedVotes);
        console.log("[VotingQuery] Mapped votes:", mappedVotes);
        const votesCount = data.num_responses;
        const totalCount = data.total_players;
        if (votesCount >= totalCount) {
          setAllVoted(true);
        }
        setVotes(mappedVotes);
        setTotalPlayers(data.total_players);


        console.log(
          `[VotingQuery] Vote Progress: ${votesCount}/${totalCount} | All voted? ${allVoted}`
        );

        if (screen === "mini-game-tiebreak") {
          return null;
        }
        if (allVoted) {

          console.log("All players voted!");
          setScreen("loading")
          setLoadingState("scenario")
          await fetchFunFacts();
          if (!scenarioData || !scenarioData.scenario) {
            console.log("Scenario not ready → go to loading screen");
            setScreen("loading");
            setLoadingState("scenario");
            await fetchFunFacts();
          } else {
            console.log("Scenario ready → show scenario");
            setScreen("scenario");
          }
        }
        return result;
      }, enabled: loadingState === "none" &&   screen !== "mini-game-tiebreak" &&
          screen !== "waiting-for-others" &&
          screen !== "winner-display",  
      refetchInterval: 300
  })


  /**
   * Handles a player's choice when answering a question.
   *
   * @param {string} answer - The key of the chosen option.
   */


  // handle choice click
  const handleChoice = async (option_id) => {
    if (!currentTurn) return;
    cancelTTS(); 
    //setShowVotes(false);
    setOptionId(option_id);
  }

  const {
    data: out,
    isLoading: isTurnLoading,
    error: turnError,
    status: turnStatus,
    } = useQuery({
      queryKey: ["scenario", playerName, roomCode, currentTurn, sessionId, roomCode, option_id, year],
      queryFn: async () => {
        console.log("submitting option", sessionId);
        const out = await submitChoice(playerName, roomCode, sessionId,currentTurn.turn_id, year, option_id);
        console.log(out)
        if (!out || !out.scenario || !out.scenario.text) {
          if (!out.room_exists) {
            setRoomDestroyed(true); 
            setScreen("destroyed");
          }
          if (!out.success) {
            console.log("not success")
            if ( out.tie && allVoted && played) {
              console.log("waiting fr others")
              setScreen("waiting-for-others");
              // setTimeout(() => {
              //   setScreen("scenario");
              // }, 5000);

              return null;
            } else if(out.tie && allVoted ) {
              console.log(allVoted);
              console.log("Tie detected, launching mini-game");
              setMiniGameOccurred(true);
              setScreen("mini-game-tiebreak");
              return null;
            } 
          }
          if (allVoted && miniGameOccurred) {
            console.log("win announcement")
            setScreen("winner-display");
            // setTimeout(() => {
            //   setScreen("scenario");
            // }, 5000);
            // console.log("announcement done")
            setMiniGameOccurred(false);
            setPlayed(false);
            // setScreen("scenario");
            return null 
        }  
          console.log("dont have scenario yet");
          return null;
      } if (allVoted && miniGameOccurred) {
            console.log("win announcement")
            setScreen("winner-display");
            // setTimeout(() => {
            //   setScreen("scenario");
            // }, 5000);
            // console.log("announcement done")
            setMiniGameOccurred(false);
            setPlayed(false);
            // setScreen("scenario");
            return null
        } 

      console.log("the data is", out );
      const mapped = {
        scenario: out.scenario.text,
        image: out.image.url
      };

      console.log("Submit choice response:", mapped);
      setScreen("scenario");
      setScenarioData(mapped);
      setYear(year + 1);
      setOptionId(null);
      return out;
    },
    enabled: currentTurn != null &&  option_id != null && screen !== "destroyed" ,
    onError: (err) => {
      console.log("onError:", err);
    }, 
    refetchInterval: 3000, 
    refetchIntervalInBackground: true, 
});



useEffect(() => {
  if (screen === "question") {
    console.log("[Animation] Resetting staged animation for new question");
    setHasAnimated(false);
    setStage(0);
  }
}, [currentTurn, screen])


// --- Staged reveal ---
  // 0 = nothing, 1 = question, 2 = option1, 3 = option2, 4 = final all
 
  useEffect(() => {
    if (screen === "question" && currentTurn) {
      setStage(1); // show question
      speak(currentTurn.question);


      const timer1 = setTimeout(() => {
        setStage(2);
        speak(currentTurn.options[0].option_text);
      }, 10000 - fadeDuration);


      const timer2 = setTimeout(() => {
        setStage(3);
        speak(currentTurn.options[1].option_text);
      }, 15000 - fadeDuration);


      const timer3 = setTimeout(() => {
        setStage(4); // show all together, no TTS
      }, 20000 - fadeDuration);


      return () => {
        clearTimeout(timer1);
        clearTimeout(timer2);
        clearTimeout(timer3);
        cancelTTS();
      };
    }
  }, [screen, currentTurn]);


const getFadeClass = (idx) => {
  switch(idx) {
    case 1: return stage === 1 || stage === 4 ? "fade-in-out show" : stage > 1 ? "fade-in-out hide" : "fade-in-out";
    case 2: return stage === 2 || stage === 4 ? "fade-in-out show" : stage > 2 ? "fade-in-out hide" : "fade-in-out";
    case 3: return stage === 3 || stage === 4 ? "fade-in-out show" : stage > 3 ? "fade-in-out hide" : "fade-in-out";
    default: return "fade-in-out";
  }
};

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



  return (
    <BasePage>
      <ExitExperience code={roomCode} player={playerName} />
      {screen == "destroyed" && (
        <RoomDestroyedPopup />
      )}
      {screen === "loading" && (
        <LoadingScreen
          isReady={isReady}
          funFacts={loadingFacts}
          onContinue={() => {
            setScreen({ loadingState });
          }}
        />
      )}
      {screen === "scenario" && scenarioData && (
        <div className="scenario-screen">

          <div className="text-container menu-glass">
          {/* Image in middle */}
          {scenarioData.image && (
            <div className="scenario-image">
              <img src={scenarioData.image} alt="scenario" className="scenario-img" />
            </div>
          )}
            <h2 className="fade-in">{scenarioData.scenario}</h2>
          </div>


          {/* Continue button at bottom */}
          <div className="scenario-footer">
            <Button
              baseButton="btn-primary"
              action={() => {
                setScreen("loading");
                setLoadingState("question");
                setAllVoted(false);
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
        <div className="question-screen">
          {/* Left side: question and choices */}
          <div className="question-main menu-glass">
            <div className="question-container">
              <h2 className={getFadeClass(1)}>{currentTurn.question}</h2>
            </div>
            <div className="choice-container">
              <Button
                baseButton={getFadeClass(2) + " choice-btn"}
                action={() => handleChoice(currentTurn.options[0].option_id)}
                title={`${currentTurn.options[0].label}. ${currentTurn.options[0].option_text}`}
              />
              <Button
                baseButton={getFadeClass(3) + " choice-btn"}
                action={() => handleChoice(currentTurn.options[1].option_id)}
                title={`${currentTurn.options[1].label}. ${currentTurn.options[1].option_text}`}
              />
            </div>
          </div>

          {/* Right side: voting display */}
          <div className="voting-sidebar">
            <VotingDisplay voters={votes} totalPlayers={totalPlayers} />
          </div>
        </div>
      )}

{screen === "mini-game-tiebreak" && !played && (
  <MiniGame
    playerName={playerName}
    roomCode={roomCode}
    turnId={currentTurn.turn_id}
    onFinish={async (score) => {
      if (played) return; // guard against duplicate replays
      console.log(`[MiniGame] ${playerName} finished with score ${score}`);

      const res = await submitTiebreakScore(playerName, roomCode, currentTurn.turn_id, score);
      console.log(res);
      setPlayed(true);

      if (res.status === "pending") {
        console.log("Waiting for other players...");
        setScreen("waiting-for-others");
        return;
      }

      if (res.status === "resolved") {
        console.log("Winner resolved:", res.winner);
        setWinnerInfo(res.winner);
        setScreen("winner-display");
        setTimeout(() => {
          setLoadingState("none");
          setScreen("scenario");
          setMiniGameOccurred(false);
          setPlayed(false);
          setWinnerInfo(null);
        }, 5000);
      }
    }}
  />
)}

      {screen === "winner-display" && winnerInfo && (
        <div className="fade-in">
          <h2>{winnerInfo} has won the round!</h2>
          <p>Their decision will be used for the next scenario.</p>
        </div>
      )}
      {screen === "waiting-for-others" && (
        <div className="waiting-screen fade-in">
          <h2>Well done {playerName}!</h2>
          <p>Please wait while other players finish their mini-game...</p>
        </div>
      )}
    </BasePage>
  );
};



export default GamePlayMulti;