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
              Welcome to 2040 <br /> <br />
              Where neurotechnology connects minds, rewrites memories, and reshapes reality. <br /> <br />
              You are the chosen voice of your people, standing between promise and peril.  <br /> <br />
              Every law you shape will ripple through lives and futures,              
              redefining what it means to be human.<br /> <br />
              Will you shield your community, pursue progress, or uphold your ethics? <br /> <br />
              The destiny of millions rests in your hands! <br /> <br />  
            </p>
          </div>
        </div>
      <div className="button-container">
      <Button baseButton="btn-back" action={() => navigate("/")} title="Back" />
      <Button baseButton="btn-primary start-fade-in" action={() => navigate("/game-play")} title="Next" />
      </div>
      </BasePage>
    );
};
export default BackgroundScreen;
