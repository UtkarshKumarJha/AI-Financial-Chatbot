import { useState } from "react";
import axios from "axios";

function App() {
  const [ticker, setTicker] = useState("");
  const [horizon, setHorizon] = useState(7);
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);

  const generateReport = async () => {
    if (!ticker) {
      alert("Enter a ticker symbol first.");
      return;
    }

    setLoading(true);
    setReport("");

    try {
      const response = await axios.post("http://127.0.0.1:8000/api/report", {
        ticker,
        horizon_days: horizon,
      });

      setReport(response.data.report);
    } catch (err) {
      setReport("Error fetching report. Your backend probably died.");
    }

    setLoading(false);
  };

  return (
    <div style={{
      width: "60%",
      margin: "auto",
      marginTop: "60px",
      fontFamily: "Arial"
    }}>
      <h1>InsighInvest Report Generator</h1>

      <div style={{ marginBottom: "20px" }}>
        <label>Ticker: </label>
        <input
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          style={{ padding: "8px", marginLeft: "10px" }}
        />
      </div>

      <div style={{ marginBottom: "20px" }}>
        <label>Horizon (days): </label>
        <input
          type="number"
          value={horizon}
          onChange={(e) => setHorizon(parseInt(e.target.value))}
          style={{ padding: "8px", marginLeft: "10px", width: "80px" }}
        />
      </div>

      <button
        onClick={generateReport}
        disabled={loading}
        style={{
          padding: "10px 16px",
          backgroundColor: "#007bff",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer"
        }}
      >
        {loading ? "Generating..." : "Generate Report"}
      </button>

      {report && (
        <div style={{
          marginTop: "40px",
          padding: "20px",
          border: "1px solid #ccc",
          borderRadius: "6px",
          whiteSpace: "pre-wrap"
        }}>
          {report}
        </div>
      )}
    </div>
  );
}

export default App;
