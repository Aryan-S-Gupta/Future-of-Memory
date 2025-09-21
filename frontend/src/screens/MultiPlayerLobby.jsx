import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { listRooms, createRoom, joinRoom } from "../../api/multiplayer/RoomManagementApi.js";
import "./GamePlay.css";
import Button from "../components/Button/Button.jsx";

const MultiplayerLobby = () => {
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
      const data = await createRoom(playerName);
      setRoomCode(data.room_code);
      console.log(roomCode);
      // Navigate to multiplayer room screen
      navigate(`/multiplayer-room/${data.room_code}?playerName=${playerName}`);
      console.log("navigated")
    };

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
      {roomList?.rooms?.map((code) => (
        <li key={code}>
          {code}
          <button onClick={() => handleJoinRoom(code)}>Join</button>
        </li>
      ))}
      </ul>
    </div>
  );
};

export default MultiplayerLobby;
