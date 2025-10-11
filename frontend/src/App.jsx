import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import MainGameScreen from "./screens/MainGameScreen.jsx";
import BackgroundScreen from "./screens/BackgroundScreen.jsx";
import HowToScreen from "./screens/HowToScreen.jsx";
import GamePlay from "./screens/GamePlay.jsx";
import MultiplayerLobby from "./screens/MultiPlayerLobby.jsx";
import GalleryScreen from "./screens/GalleryScreen.jsx";

import '@fontsource/kanit/400.css';
import '@fontsource/kanit/500.css';
import '@fontsource/orbitron/500.css'; // NEW

import BackgroundWrapper from "./screens/BasePage.jsx";
import AudioProvider from "./audio/AudioProvider.jsx";
import mainTheme from "./assets/Heaven_DavidFesliyan.mp3";
import galleryTheme from "./assets/DeepMeditation_DavidFesliyan.mp3";
import { SessionProvider } from "../SessionContext.jsx";
import IdleHomeReset from "./components/IdleHomeReset.jsx";

function App() {
  const routeAudioMap = {
    "/gallery*": [
      { src: mainTheme, loop: true, volume: 0.1 },
      { src: galleryTheme, loop: true, volume: 0.2 },
    ],
    "*": [{ src: mainTheme, loop: true }],
  };

  return (
    <Router>
      <AudioProvider routeAudioMap={routeAudioMap} crossfadeMs={1000} initialVolume={0.38}>
        <BackgroundWrapper>
          <SessionProvider>
            <IdleHomeReset idleMs={600000} />
            <Routes>
              <Route path="/" element={<MainGameScreen />} />
              <Route path="/story" element={<BackgroundScreen />} />
              <Route path="/how-to-play" element={<HowToScreen />} />
              <Route path="/game-play" element={<GamePlay />} />
              <Route path="/multiplayer-lobby" element={<MultiplayerLobby />} />
              <Route path="/gallery/:sessionId" element={<GalleryScreen />} />
            </Routes>
          </SessionProvider>
        </BackgroundWrapper>
      </AudioProvider>
    </Router>
  );
}

export default App;