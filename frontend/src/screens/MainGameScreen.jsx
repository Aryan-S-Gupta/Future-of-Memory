import { useNavigate } from "react-router-dom";
import BasePage from "../components/BasePage/BasePage.jsx";
import Button from "../components/Button/Button.jsx";

const MainGameScreen = () => {
  const navigate = useNavigate();

  return (
    <BasePage>
      <h1 className="title">Future of Memory</h1>
      <div className="button-group">
        <Button baseButton="btn-primary" action={() => navigate("/story")} title="Start" />
        <Button baseButton="btn-secondary" action={() => navigate("/how-to-play")} title="How To Play"/>
      </div>
    </BasePage>
  );
};

export default MainGameScreen;