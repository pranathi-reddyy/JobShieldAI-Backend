import "./App.css";
import { useState } from "react";

function App() {
  const [description, setDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false); // Track network request state

  const analyzeJob = async () => {
    if (!description.trim()) {
      alert("Please paste a job description first!");
      return;
    }

    setLoading(true);
    setResult(null); // Clear previous result during a new scan

    try {
      const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          description: description,
        }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error connecting to JobShield AI Backend:", error);
    } finally {
      setLoading(false);
    }
  };

  // Maps backend predictions directly to clean branding hex colors
  const getPredictionColor = () => {
    if (result?.prediction === "Fake") return "#ef4444"; // Vivid Red
    if (result?.prediction === "Suspicious") return "#f59e0b"; // Alert Amber/Yellow
    return "#22c55e"; // Safe Green
  };

  const dynamicColor = getPredictionColor();

  return (
    <div className="container">
      <div className="card">
        <h1 className="title">🛡️ JobShield AI</h1>

        <p className="subtitle">
          Detect Fake Job Offers Before You Apply
        </p>

        <textarea
          rows="10"
          placeholder="Paste Job Description, Email content, or Google Form text requirements here..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={loading}
        />

        <button onClick={analyzeJob} disabled={loading}>
          {loading ? "Analyzing Text Patterns..." : "Analyze Job"}
        </button>

        {result && (
          <div className="result-card">
            {/* Dynamic style injections replace hardcoded class rules */}
            <h2 style={{ color: dynamicColor }}>
              {result.prediction}
            </h2>

            <p>
              <strong>Confidence:</strong> {result.confidence}%
            </p>

            <div className="risk-bar" style={{ backgroundColor: "#172A45" }}>
              <div
                className="risk-fill"
                style={{
                  width: `${result.confidence}%`,
                  backgroundColor: dynamicColor,
                  height: "100%",
                  borderRadius: "4px",
                  transition: "width 0.5s ease-in-out" // Makes the bar slide smoothly
                }}
              ></div>
            </div>
            
            <h3>Analysis Report</h3>

            <ul>
              {result.reasons?.map((reason, index) => (
                <li key={index} style={{ marginBottom: "6px" }}>
                  {reason}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;