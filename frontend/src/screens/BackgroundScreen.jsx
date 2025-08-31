import { useNavigate } from "react-router-dom";
import BasePage from "../components/BasePage/BasePage.jsx";
import Button from "../components/Button/Button.jsx";
import "./BackgroundScreen.css";


const BackgroundScreen = () => {
  const navigate = useNavigate();

  /*
    HowToScreen component provides instructions on how to play the game.
  */
  return (
    <BasePage>
      <h1 className="title">Background</h1>
      <div className="crawl-container">
        <div className="crawl-text">
          <p> 
            The year is 2040. Neurotechnology has shattered boundaries: <br /> <br />
            memories can be rewritten, emotions dialed up or down, consciousness linked and shared across minds. <br /> <br />
            At the Global Neurotechnology Regulation Authority, your decisions shapes the way people live,  <br /> <br />
            the paths societies will take, and what humanity might become. <br /> <br />
            Progress and profit drive innovation, but freedom collides with the need for control. <br /> <br />
            Ethics blur in the face of possibilities. The world is watching! <br /> <br />
            SO CHOOSE WISELY! <br /> <br />  
          </p>
        </div>
      </div>
      <div className="button-container">
      <Button baseButton="btn-back" action={() => navigate("/")} title="Back" />
      <Button baseButton="btn-primary start-fade-in" action={() => navigate("/game-play")} title="Start" />
      </div>
      </BasePage>
    );
};
export default BackgroundScreen;
