import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import MainGameScreen from "./screens/MainGameScreen.jsx";
import StoryScreen from "./screens/StoryScreen.jsx";
import HowToScreen from "./screens/HowToScreen.jsx";


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainGameScreen />} />
        <Route path="/story" element={<StoryScreen />} />
        <Route path="/how-to-play" element={<HowToScreen/>} />
      </Routes>
    </Router>
  );
}

export default App;