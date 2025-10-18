import { useState } from "react";
import BasePage from "../../screens/BasePage.jsx";
import Button from "../../components/Button/Button.jsx";
import "../../styles/FeedbackScreen.css";
import { useNavigate } from "react-router-dom";
import { submitFeedback } from "../../../api/single-player/FeedbackApi";

/**
 * FeedbackScreen component
 *
 * Provides a user interface to collect:
 * - Ratings for 5 questions (scale 1–5 with subheadings)
 * - Open-ended text feedback
 *
 * On submit, sends the collected feedback to the backend as JSON.
 */
const FeedbackScreen = () => {
  const navigate = useNavigate();
  const questions = [
    "How clear was the game's story?",
    "How engaging were the choices in the game?",
    "How immersive did you find the visuals and interface?",
    "How intuitive was the game navigation?",
    "Overall, how satisfied are you with the game experience?"
  ];

  const ratingLabels = ["Unclear", "Somewhat Clear", "Neutral", "Clear", "Excellent"];

  const [ratings, setRatings] = useState(Array(questions.length).fill(0));
  const [feedbackText, setFeedbackText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  const handleRating = (qIndex, value) => {
    const newRatings = [...ratings];
    newRatings[qIndex] = value;
    setRatings(newRatings);
  };

  const handleSubmit = async () => {
    const feedbackData = {
      ratings: questions.map((q, i) => ({
        question: q,
        rating: ratings[i] || null
      })),
      comments: feedbackText,
    };

    try {
      setSubmitting(true);
      await submitFeedback(feedbackData);
      setSuccessMessage("Thank you — your feedback has been saved.");
      setRatings(Array(questions.length).fill(0));
      setFeedbackText("");
    } catch (err) {
      console.error(err);
      setSuccessMessage("");
      alert("Error submitting feedback. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <BasePage>
      <div className="button-group">
        <Button baseButton="btn-exit" action={() => navigate("/")} title="Back" />
      </div>
      <div className="feedback-screen">
        <h1 className="feedback-title">Player Feedback</h1>
        <form className="feedback-form" onSubmit={(e) => e.preventDefault()}>
          {questions.map((q, i) => (
            <div key={i} className="feedback-question">
              <p>{q}</p>
              <div className="rating">
                <div className="rating-buttons">
                  {Array(5)
                    .fill(0)
                    .map((_, idx) => (
                      <button
                        key={idx}
                        type="button"
                        className={`rating-btn ${ratings[i] === idx + 1 ? "active" : ""}`}
                        onClick={() => handleRating(i, idx + 1)}
                      >
                        {idx + 1}
                      </button>
                    ))}
                </div>
                <div className="rating-labels" style={{ display: "flex", justifyContent: "space-between", marginTop: "0.3rem" }}>
                  {ratingLabels.map((label, idx) => (
                    <span key={idx} className="rating-label">{label}</span>
                  ))}
                </div>
              </div>
            </div>
          ))}

          <textarea
            className="feedback-textarea"
            placeholder="Additional feedback (optional)..."
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
          />

          <button
            className="btn-submit-feedback"
            onClick={handleSubmit}
            disabled={submitting}
          >
            {submitting ? "Submitting..." : "Submit Feedback"}
          </button>
          {successMessage && <div className="feedback-success">{successMessage}</div>}
        </form>
      </div>
    </BasePage >
  );
};

export default FeedbackScreen;
