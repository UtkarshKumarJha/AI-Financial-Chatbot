import { useState } from "react";
import { TrendingUp, FileText, Calendar, Search } from "lucide-react";

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
      const response = await fetch("http://127.0.0.1:8000/api/report", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ticker,
          horizon_days: horizon,
        }),
      });

      const data = await response.json();
      setReport(data.report);
    } catch (err) {
      setReport("Error fetching report. Check your backend connection.");
    }

    setLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      generateReport();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Animated background effect */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDE2YzAtNi42MjcgNS4zNzMtMTIgMTItMTJzMTIgNS4zNzMgMTIgMTItNS4zNzMgMTItMTIgMTItMTItNS4zNzMtMTItMTJ6TTAgMTZjMC02LjYyNyA1LjM3My0xMiAxMi0xMnMxMiA1LjM3MyAxMiAxMi01LjM3MyAxMi0xMiAxMlMwIDIyLjYyNyAwIDE2eiIvPjwvZz48L2c+PC9zdmc+')] opacity-30"></div>

      <div className="relative max-w-6xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <TrendingUp className="w-12 h-12 text-purple-400" />
            <h1 className="text-5xl font-bold text-white">
              InsightInvest
            </h1>
          </div>
          <p className="text-purple-200 text-lg">
            AI-Powered Investment Analysis & Reporting
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl border border-white/20 p-8 mb-8">
          <div className="grid md:grid-cols-2 gap-6 mb-6">
            {/* Ticker Input */}
            <div>
              <label className="flex items-center gap-2 text-purple-200 font-medium mb-3">
                <Search className="w-5 h-5" />
                Stock Ticker
              </label>
              <input
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                onKeyPress={handleKeyPress}
                placeholder="e.g., AAPL, MSFT, GOOGL"
                className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-lg text-white placeholder-purple-300/50 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              />
            </div>

            {/* Horizon Input */}
            <div>
              <label className="flex items-center gap-2 text-purple-200 font-medium mb-3">
                <Calendar className="w-5 h-5" />
                Forecast Horizon (Days)
              </label>
              <input
                type="number"
                value={horizon}
                onChange={(e) => setHorizon(parseInt(e.target.value) || 7)}
                onKeyPress={handleKeyPress}
                min="1"
                max="365"
                className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              />
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={generateReport}
            disabled={loading}
            className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transform hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                Generating Analysis...
              </>
            ) : (
              <>
                <FileText className="w-5 h-5" />
                Generate Investment Report
              </>
            )}
          </button>
        </div>

        {/* Report Display */}
        {report && (
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl border border-white/20 p-8 animate-fade-in">
            <div className="flex items-center gap-3 mb-6 pb-4 border-b border-white/20">
              <FileText className="w-6 h-6 text-purple-400" />
              <h2 className="text-2xl font-bold text-white">
                Analysis Report
              </h2>
            </div>
            <div className="prose prose-invert max-w-none">
              <pre className="text-purple-100 whitespace-pre-wrap leading-relaxed font-sans text-base">
                {report}
              </pre>
            </div>
          </div>
        )}

        {/* Footer */}
        {!loading && !report && (
          <div className="text-center text-purple-300/60 mt-12">
            <p className="text-sm">
              Enter a ticker symbol and forecast horizon to generate your investment analysis
            </p>
          </div>
        )}
      </div>

      <style>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fade-in {
          animation: fade-in 0.5s ease-out;
        }
      `}</style>
    </div>
  );
}

export default App;