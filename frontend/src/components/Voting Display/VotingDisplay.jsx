import React from "react";
import "../../styles/VotingDisplay.css";

const VotingDisplay = ({ voters = [], totalPlayers }) => {
  const votedCount = voters.filter((v) => v.hasVoted).length;
  const progress = (votedCount / totalPlayers) * 100;

  return (
    <div className="voting-display">
      <h3 className="voting-title">
        Votes in: {votedCount} / {totalPlayers}
      </h3>

      {/* Progress Bar */}
      <div className="voting-progress">
        <div
          className="voting-progress-fill"
          style={{ width: `${progress}%` }}
        ></div>
      </div>

      {/* Player badges */}
      <div className="voting-players">
        {voters.map((player, i) => (
          <div
            key={player.id ? player.id : `${player.name}-${i}`}
            className={`voting-player ${player.hasVoted ? "voted" : ""}`}
          >
            {player.name}
          </div>
        ))}
      </div>
    </div>
  );
};

export default VotingDisplay;
