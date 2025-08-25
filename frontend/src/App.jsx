import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import MainGameScreen from "./screens/MainGameScreen.jsx";
import BackgroundScreen from "./screens/BackgroundScreen.jsx";
import HowToScreen from "./screens/HowToScreen.jsx";
import '@fontsource/kanit/400.css';
import '@fontsource/kanit/500.css';

import BackgroundWrapper from "./components/BasePage/BasePage.jsx";

function App() {
  return (
    <BackgroundWrapper>
      <Router>
        <Routes>
          <Route path="/" element={<MainGameScreen />} />
          <Route path="/story" element={<BackgroundScreen />} />
          <Route path="/how-to-play" element={<HowToScreen />} />
        </Routes>
      </Router>
    </BackgroundWrapper>
  );
}

export default App;