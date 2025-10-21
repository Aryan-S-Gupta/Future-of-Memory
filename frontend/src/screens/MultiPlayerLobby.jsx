import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { listRooms, createRoom, joinRoom } from "../../api/multiplayer/RoomManagementApi.js";
import "../styles/MultiplayerLobby.css"; // Import CSS for styling
import Button from "../components/Button/Button.jsx";
import BasePage from "./BasePage.jsx";
import { useSession } from "../../SessionContext.jsx";
import { startPrerender } from "../../api/single-player/GameApi.js";

/**
 * MultiplayerLobby Component
 * 
 * This component renders the multiplayer lobby screen where users can:
 *  - Enter their nickname.
 *  - Create a new multiplayer room for collaboration
 *  - View the list of available rooms.
 *  - Join an existing room using the codes provided on the screen.
 * 
 * The component uses React Query to fetch the list of rooms from the backend
 * and React Router's `useNavigate` for programmatic navigation to rooms.
 * Local state is used to manage the player's name and the current room code.
 */
const MultiplayerLobby = () => {
  // Local state to store player name and room code
  const [playerName, setPlayerName] = useState("");
  const [roomCode, setRoomCode] = useState("");
  const { sessionId, setSessionId } = useSession();
  const [mode, setMode] = useState("host"); // "peer" or "host"
  const [alertMsg, setAlertMsg] = useState(null);
  const [promptOpen, setPromptOpen] = useState(false);
  const [pendingRoom, setPendingRoom] = useState(null);

  const navigate = useNavigate();

  // Fetch list of available rooms using React Query
  const {
    data: roomList,
    isLoading: isRoomsLoading,
    error: roomError,
  } = useQuery({
    queryKey: ["rooms"],
    queryFn: () => listRooms(),
  });

  /**
   * Handle creating a new multiplayer room.
   * - Ensures the player enters a nickname.
   * - Calls API to create a new room.
   * - Updates local state with the room code.
   * - Navigates to the created room.
   */
  const handleCreateRoom = async () => {
    if (!playerName) {
      return setAlertMsg("Please enter a nickname before creating a room.");

    }
    const data = await createRoom(playerName, mode);
    setSessionId(data.session_id);
    await startPrerender(data.session_id, 2035);
    setRoomCode(data.room_code);
    console.log(roomCode);
    if (mode === "peer") {
      navigate(`/background-multi/${data.room_code}/${playerName}`);
    } else {
      navigate(`/projection-host/${data.room_code}/${playerName}/${playerName}/${mode}`);
    }
    // Navigate to multiplayer room screen
    // navigate(`/multiplayer-room/${data.room_code}/${playerName}`);
    console.log("navigated with session id " + data.session_id);
  };


  const handleJoinRoom = (code) => {
    setPendingRoom(code);
    setPromptOpen(true);
  };

  const joinWithName = async (name) => {
    if (!name) {
      setAlertMsg("Please enter your name to join the room.");
      return;
    }
    setPromptOpen(false);
    setRoomCode(pendingRoom);
    setPlayerName(name);

    try {
      const data = await joinRoom(pendingRoom, name);
      if (data.success === "True") {
        setSessionId(data.session_id);
        console.log("session id is " + data.session_id);
        console.log("the host of this room is: " + data.host);
        console.log("the game has started? " + data.game_started);

        if (data.mode === "host") {
          if (data.game_started === "False") {
            navigate(`/projection-host/${pendingRoom}/${name}/${data.host}/${mode}`);
          } else {
            setAlertMsg("Session already in progress. Please join another room.");
          }
        } else {
          navigate(`/background-multi/${pendingRoom}/${name}&mode=${mode}`);
        }
      } else {
        setAlertMsg("Unable to join the room. Please try again.");
      }
    } catch (err) {
      console.error(err);
      setAlertMsg("Error joining room. Please try again.");
    }
  };


  return (
    <BasePage>
      <div className="multiplayer-lobby">
        <h2 className="title">Multiplayer Lobby</h2>
        <div className="room-input-container">
          <div className="input-row">
            <input
              className="player-input"
              type="text"
              placeholder="Enter your name"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
            />
            <button className="btn-create-room" onClick={handleCreateRoom}>
              Create Room
            </button>
          </div>

        </div>


        <h3 className="subheading">Available Rooms</h3>
        <ul className="room-list">
          {roomList?.rooms?.map((code) => (
            <li key={code} className="room-item">
              <span className="room-code">{code}</span>
              <button className="btn-create-room" onClick={() => handleJoinRoom(code)}>Join</button>
            </li>
          ))}
        </ul>
        <div className="button-container">
          <Button baseButton="btn-exit" action={() => navigate("/")} title="Back" />
        </div>
      </div>
      {/* === Custom Alert Modal === */}
      {alertMsg && (
        <div className="modal-overlay">
          <div className="modal-box">
            <h3>⚠️ Notice</h3>
            <p>{alertMsg}</p>
            <button className="btn-modal" onClick={() => setAlertMsg(null)}>OK</button>
          </div>
        </div>
      )}

      {/* === Custom Prompt Modal === */}
      {promptOpen && (
        <div className="modal-overlay">
          <div className="modal-box">
            <h3>Enter your name to join</h3>
            <input
              className="modal-input"
              type="text"
              placeholder="Your nickname"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
            />
            <div className="modal-actions">
              <button className="btn-modal" onClick={() => joinWithName(playerName)}>Join</button>
              <button className="btn-modal cancel" onClick={() => setPromptOpen(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}

    </BasePage >
  );
};

export default MultiplayerLobby;



