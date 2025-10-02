import React from "react";
import Button from "../Button/Button.jsx";
import "../../styles/LoadingScreen.css";

/**
 * LoadingScreen component
 *
 * Props:
 * - isReady: boolean, true if scenario and image are ready
 * - funFacts: array of { fact, link, link_text } objects
 * - onContinue: function to call when user clicks continue
 */
const LoadingScreen = ({ isReady, funFacts = [], onContinue }) => {
  return (
    <div className="loading-screen">
      {!isReady && <h2>Please wait while we are generating your world...</h2>}

      {funFacts.length > 0 && (
        <div className="fun-facts">
          <h3>Did you know?</h3>
          <ul>
            {funFacts.map((fact, i) => (
              <li key={i}>
                {fact.fact}{" "}
                {fact.link && (
                  <a href={fact.link} target="_blank" rel="noreferrer">
                    {fact.link_text || "Learn more"}
                  </a>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {isReady && (
        <div className="loading-footer">
          <p>Your work is now ready, press continue to view</p>
          <Button baseButton="btn-primary" action={onContinue} title="Continue" />
        </div>
      )}
    </div>
  );
};

export default LoadingScreen;
