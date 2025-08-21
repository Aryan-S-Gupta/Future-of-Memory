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
      <div className="text-container2">
      <p className="text"> 
        The year is 2040.
        Neurotechnology has advanced beyond imagination, allowing memories to be <br /> <br />
        edited, emotions regulated, and even consciousness shared. These breakthroughs have brought <br /> <br />
        progress, but also deep ethical uncertainty. You are a senior decision-maker at the Global <br /> <br />
        Neurotechnology Regulation Authority (GNRA). Your responsibility: evaluate new applications of <br /> <br /> 
        neurotech and decide whether they should be encouraged, restricted, or banned. Every choice <br /> <br /> 
        you make will ripple outward, shaping how societies evolve, how people live, and how humanity <br /> <br />
        defines itself in this new age of the mind. Your task is not simple. Progress, profit, freedom, and <br /> <br />
        control are all at stake. The future of human thought begins with your decisions.
      </p>
      </div>
      <div className="button-group">
        <Button baseButton="btn-back" action={() => navigate("/")} title="Back" />
      </div>
    </BasePage>
  );
};
export default BackgroundScreen;
