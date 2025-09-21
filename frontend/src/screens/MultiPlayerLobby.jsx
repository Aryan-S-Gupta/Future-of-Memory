import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { listRooms, createRoom, joinRoom } from "../../api/multiplayer/GameFlowApi.js";
import "./GamePlay.css";
import Button from "../components/Button/Button.jsx";

const MultiplayerLobby = () => {
    const [rooms, setRooms] = useState([]);
    const [playerName, setPlayerName] = useState("");
    const [roomCode, setRoomCode] = useState("");
    const navigate = useNavigate();

    const {
        data: roomList,
        isLoading: isRoomsLoading,
        error: roomError,
    } = useQuery({
        queryKey: ["rooms"],
        queryFn: () => listRooms(),
    });

    const handleCreateRoom = async () => {
        if (!playerName) {
            return alert("Please Enter a NickName");
        }
        
      const response = await createRoom(playerName);
      setRoomCode(response.data.room_code);
      console.log(roomCode);
      // Navigate to multiplayer room screen
      navigate(`/multiplayer-room/${response.data.room_code}?playerName=${playerName}`);
      console.log("navigated")
    };

  const handleJoinRoom = async (code) => {
    if (!playerName) {
      return alert("Enter your name first!");
    }
    const response = await joinRoom(code, playerName);
    if (response.data.success){
      setRoomCode(code);
      navigate(`/multiplayer-room/${code}?playerName=${playerName}`);
    } else {
      <div> We are Sorry, We are unable to add you to the requested room. Please Try again</div>
    }
  };

  return (
    <div>
      <Button baseButton="btn-back" action={() => navigate("/")} title="Back" />
      <h2>Multiplayer Lobby</h2>
      <input
        type="text"
        placeholder="Your Name"
        value={playerName}
        onChange={(e) => setPlayerName(e.target.value)}
      />
      <button onClick={handleCreateRoom}>Create Room</button>

      <h3>Available Rooms</h3>
      <ul>
          {Object.entries(roomList).map((room) => (
          <li key={room.code}>
            {room.code} ({room.players.length} players)
            <button onClick={() => handleJoinRoom(room.code)}>Join</button>
          </li>
            ))}
      </ul>
    </div>
  );
};

export default MultiplayerLobby;
