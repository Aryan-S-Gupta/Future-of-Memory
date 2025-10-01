import "../BasePage/BasePage.css";
import LetterGlitch from "../Dynamic Background/LetterGlitch";

/**
 * BasePage component
 *
 * This is a reusable layout wrapper for different screens in the app.
 * It provides:
 * - A full-screen background layer with the `LetterGlitch` animated effect.
 * - A content container that renders whatever child components are passed in.
 *
 * @component
 * @param {Object} props
 * @param {React.ReactNode} props.children - The content to render in the foreground layer.
 *
 * @returns {JSX.Element} A styled screen wrapper with background animation and child content.
 */
export default function BasePage({ children }) {
  return (
    <div className="screen">
      {/* Background layer with glitch animation effect.
          Positioned absolutely to fill the entire screen behind content. */}
      <div className="bg-layer" aria-hidden="true" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: -1 }}>
        <LetterGlitch
          glitchSpeed={0}
          centerVignette={true}
          outerVignette={true}
          smooth={false}
        />
      </div>

      {/* Foreground content container where page-specific children are rendered */}
      <div className="content">
        {children}
      </div>
    </div>
  );
}