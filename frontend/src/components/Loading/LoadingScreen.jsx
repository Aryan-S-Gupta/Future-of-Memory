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
const LoadingScreen = ({ funFacts = [], onContinue, setScreen,  }) => {
  return (
    <div className="loading-screen">
        <div className="loading-container">
          <h2 className="loading-title">
            Please wait while we are generating your world...
          </h2>

          {/* Futuristic loading bar */}
          <div className="loading-bar-wrapper">
            <div className="loading-bar"></div>
          </div>

          {funFacts.length > 0 && (
            <div className="fun-facts-section">
              <h3 className="fun-facts-title">Did you know?</h3>
              <div className="fun-facts-list">
                {funFacts.map((fact, i) => (
                  <div key={i} className="fun-fact-item">
                    <p className="fun-fact-text">{fact.fact}</p>
                    {fact.link && (
                      <p className="fun-fact-link">
                        Visit{" "}
                        <a href={fact.link} target="_blank" rel="noreferrer">
                          {fact.link_text || fact.link}
                        </a>{" "}
                        to read more.
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
    </div>
  );
};

export default LoadingScreen;