import "../BasePage/BasePage.css";
import LetterGlitch from "../Dynamic Background/LetterGlitch";

export default function BasePage({ children }) {
  return (
    <div className="screen">
      {/* Background layer */}
      <div className="bg-layer" aria-hidden="true" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: -1 }}>
        <LetterGlitch
          glitchSpeed={0}
          centerVignette={true}
          outerVignette={true}
          smooth={false}
        />
      </div>

      {/* Foreground content */}
      <div className="content">
        {children}
      </div>
    </div>
  );
}