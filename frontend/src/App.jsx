import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import MainGameScreen from "./screens/MainGameScreen.jsx";
import StoryScreen from "./screens/StoryScreen.jsx";
import HowToScreen from "./screens/HowToScreen.jsx";
import GamePlay from "./screens/GamePlay.jsx";
import '@fontsource/kanit/400.css';
import '@fontsource/kanit/500.css';

import BackgroundWrapper from "./components/BasePage/BasePage.jsx";

function App() {
  return (
    <BackgroundWrapper>
      <Router>
        <Routes>
          <Route path="/" element={<MainGameScreen />} />
          <Route path="/story" element={<StoryScreen />} />
          <Route path="/how-to-play" element={<HowToScreen />} />
          <Route path="/game-play" element={<GamePlay/>} />
      </Routes>
      </Router>
    </BackgroundWrapper>
  );
}

export default App;