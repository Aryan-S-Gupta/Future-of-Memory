import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { listRooms, createRoom, joinRoom } from "../../api/multiplayer/RoomManagementApi.js";
import "./MultiplayerLobby.css"; // Import CSS for styling
import Button from "../components/Button/Button.jsx";
import BasePage from "../components/BasePage/BasePage.jsx";

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
        return alert("Please Enter a NickName");
    }
    const data = await createRoom(playerName);
    setRoomCode(data.room_code);
    console.log(roomCode);
    // Navigate to multiplayer room screen
    navigate(`/multiplayer-room/${data.room_code}?playerName=${playerName}`);
    console.log("navigated")
  };

  /**
   * Handle joining an existing multiplayer room.
   * - Prompts the user for a name.
   * - Calls API to join the specified room.
   * - Updates local state with player name and room code.
   * - Navigates to the joined room on success.
   *
   * @async
   * @param {string} code - The room code to join.
   * @returns {Promise<void>}
   */
  const handleJoinRoom = async (code) => {
    const name = window.prompt("Enter your name to join the room:");
    if (!name) {
      alert("Sorry");
    }
    setRoomCode(code);
    setPlayerName(name); 
    try {
      const data = await joinRoom(code, name);
      if (data.success == "True") {
        navigate(`/multiplayer-room/${code}?playerName=${name}`);
        console.log("navigated")
      } else {
        alert("Sorry, unable to join the room. Please try again.");
      }
    } catch (err) {
      console.error(err);
      alert("Error joining room. Please try again.");
    }
  };

  return (
    <BasePage>
    <div className="multiplayer-lobby">
    <h2 className="title">Multiplayer Lobby</h2>
      <div className="room-input-container">
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
    <h3 className="subheading">Available Rooms</h3>
    <ul className="room-list">
      {roomList?.rooms?.map((code) => (
        <li key={code} className="room-item">
          <span className="room-code">{code}</span>
          <button className="btn-join-room" onClick={() => handleJoinRoom(code)}>Join</button>
        </li>
        ))}
    </ul>
    <div className="button-container">
      <Button baseButton="btn-back" action={() => navigate("/")} title="Back" />
    </div>
  </div>
  </BasePage>
  );
};

export default MultiplayerLobby;
