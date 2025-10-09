import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import MainGameScreen from "./screens/MainGameScreen.jsx";
import BackgroundScreen from "./screens/BackgroundScreen.jsx";
import BackgroundScreenMulti from "./screens/BackgroundScreenMulti.jsx";
import HowToScreen from "./screens/HowToScreen.jsx";
import GamePlay from "./screens/GamePlay.jsx";
import MultiplayerLobby from "./screens/MultiPlayerLobby.jsx";
import '@fontsource/kanit/400.css';
import '@fontsource/kanit/500.css';
import GamePlayMulti from "./screens/GamePlayMulti.jsx";
import HostScreen from "./screens/HostScreen.jsx";
import FeedbackScreen from "./components/FeedbackScreen/FeedbackScreen.jsx";
import BackgroundWrapper from "./screens/BasePage.jsx";
import AudioProvider from "./audio/AudioProvider.jsx";
import mainTheme from "./assets/Heaven_DavidFesliyan.mp3";
import { SessionProvider } from "../SessionContext.jsx";

function App() {

  const routeAudioMap = {
    "*": { src: mainTheme, loop: true },
  };

  return (
    <Router>
      <AudioProvider routeAudioMap={routeAudioMap} crossfadeMs={1000} initialVolume={0.38}>
        <BackgroundWrapper>
          <SessionProvider>
            <Routes>
              <Route path="/" element={<MainGameScreen />} />
              <Route path="/story" element={<BackgroundScreen />} />
              <Route path="/how-to-play" element={<HowToScreen />} />
              <Route path="/game-play" element={<GamePlay />} />
              <Route path="/multiplayer-lobby" element={<MultiplayerLobby/>} />
              <Route path="/background-multi/:roomCode" element={<BackgroundScreenMulti/>} />
              <Route path="/feedback" element={<FeedbackScreen/>} />
              <Route path="/multiplayer-room/:roomCode" element={<GamePlayMulti />} />
              <Route path="/multiplayer-room/:roomCode/:playerName" element={<HostScreen />} />
            </Routes>
          </SessionProvider>
        </BackgroundWrapper>
      </AudioProvider>
    </Router >
  );
}

export default App;