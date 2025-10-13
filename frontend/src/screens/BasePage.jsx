import "../styles/BasePage.css";
import GlobalToolbar from "../components/TopBar/GlobalToolbar";

import bgJpg from "../assets/bg.jpg";

/**
 * BasePage component
 *
 * This is a reusable layout wrapper for different screens in the app.
 * It provides:
 * - A full-screen background layer (now a static image via CSS background-image).
 * - A content container that renders whatever child components are passed in.
 *
 * @component
 * @param {Object} props
 * @param {React.ReactNode} props.children - The content to render in the foreground layer.
 *
 * @returns {JSX.Element} A styled screen wrapper with background image and child content.
 */
export default function BasePage({ children }) {
  //  the image cache so it appears quicker on first screen
  // (keeps code minimal; safe to remove if you prefer zero JS here)
  // eslint-disable-next-line no-unused-vars
  const _ = (() => {
    const img = new Image();
    img.src = bgJpg;
  })();

  return (
    // Apply the single JPG as background (CSS handles cover/center/no-repeat)
    <div className="screen" style={{ backgroundImage: `url(${bgJpg})` }}>
      {/* Background layer kept for structure/stacking, but no animated component now. */}
      <div className="bg-layer" aria-hidden="true" />

      {/* Global top-right toolbar*/}
      <GlobalToolbar />

      {/* Foreground content container where page-specific children are rendered */}
      <div className="content">
        {children}
      </div>
    </div>
  );
}