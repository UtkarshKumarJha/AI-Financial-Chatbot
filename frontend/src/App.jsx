import React, { useState } from "react";
import axios from 'axios';
import { 
  TrendingUp, 
  Search, 
  Loader2, 
  MessageSquare, 
  ArrowRight,
  Sparkles
} from "lucide-react";
import StockChart from './components/StockChart';
import AnalysisCard from './components/AnalysisCard';

function App() {
  // State for inputs
  const [ticker, setTicker] = useState("");
  const [question, setQuestion] = useState("");
  const [horizon, setHorizon] = useState(7);
  
  // State for response
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generateReport = async () => {
    if (!ticker) {
      setError("Please enter a ticker symbol (e.g., AAPL) to begin.");
      return;
    }

    setLoading(true);
    setError("");
    setReport(null);

    try {
      // Construct the user input based on whether they typed a question
      // If box is empty, default to "Analyze [Ticker] stock"
      const finalQuery = question.trim() 
        ? question 
        : `Analyze ${ticker} stock performance and outlook.`;

      const response = await axios.post("http://127.0.0.1:8000/api/chat", {
        user_input: finalQuery,
        ticker: ticker,
        horizon_days: horizon,
      });

      setReport(response.data);
    } catch (err) {
      console.error(err);
      setError("Connection failed. Ensure the backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-purple-500/30 pb-20">
      
      {/* --- BACKGROUND EFFECTS --- */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-900/20 rounded-full blur-[120px]"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-900/10 rounded-full blur-[120px]"></div>
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
      </div>

      <div className="relative z-10 max-w-5xl mx-auto px-4 md:px-6 py-12">
        
        {/* --- HEADER --- */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center gap-3 mb-6 bg-slate-900/50 border border-slate-700/50 p-2 pr-6 rounded-full backdrop-blur-sm">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full flex items-center justify-center shadow-lg">
                <TrendingUp className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white">InsightInvest</span>
          </div>
          
          <h1 className="text-4xl md:text-6xl font-extrabold text-white mb-6 tracking-tight leading-tight">
            The AI Analyst That <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-blue-400 to-emerald-400 animate-gradient">
              Really Understands
            </span>
          </h1>
          <p className="text-slate-400 text-lg max-w-xl mx-auto">
            Combine real-time news, quarterly fundamentals, and quantitative predictive modeling into one actionable report.
          </p>
        </div>

        {/* --- RESEARCH COMMAND CENTER --- */}
        <div className="max-w-3xl mx-auto mb-16 bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-6 shadow-2xl">
          
          {/* Top Row: Ticker & Horizon */}
          <div className="flex flex-col sm:flex-row gap-4 mb-4">
            <div className="relative flex-1 group">
                <Search className="absolute left-4 top-3.5 text-slate-500 w-5 h-5 group-focus-within:text-purple-400 transition-colors" />
                <input
                    type="text"
                    value={ticker}
                    onChange={(e) => setTicker(e.target.value.toUpperCase())}
                    placeholder="Ticker Symbol (e.g. NVDA)"
                    className="w-full bg-slate-950/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all font-bold tracking-wide"
                />
            </div>
            
            <div className="relative w-full sm:w-48 group">
                <div className="absolute left-4 top-3.5 text-slate-500 text-xs font-bold uppercase tracking-wider pointer-events-none">
                    Horizon
                </div>
                <input 
                    type="number" 
                    value={horizon}
                    onChange={(e) => setHorizon(parseInt(e.target.value))}
                    className="w-full bg-slate-950/50 border border-slate-700 rounded-xl pl-20 pr-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all font-mono"
                    min="1" max="30"
                />
                <div className="absolute right-4 top-3.5 text-slate-500 text-sm pointer-events-none">Days</div>
            </div>
          </div>

          {/* Middle Row: Natural Language Question */}
          <div className="relative mb-6 group">
            <MessageSquare className="absolute left-4 top-4 text-slate-500 w-5 h-5 group-focus-within:text-blue-400 transition-colors" />
            <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a specific question (optional)... &#10;Ex: 'How will the new AI chip announcements affect margins?'"
                className="w-full bg-slate-950/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all resize-none h-28 leading-relaxed"
            />
          </div>

          {/* Action Button */}
          <button
            onClick={generateReport}
            disabled={loading}
            className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white py-4 rounded-xl font-bold text-lg shadow-lg shadow-purple-900/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform active:scale-[0.99] flex items-center justify-center gap-2 group"
          >
            {loading ? (
                <>
                    <Loader2 className="animate-spin w-6 h-6"/> 
                    Running Analysis...
                </>
            ) : (
                <>
                    <Sparkles className="w-5 h-5 text-yellow-300" />
                    Generate Research Report
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </>
            )}
          </button>

          {error && (
            <div className="mt-4 p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm text-center rounded-lg animate-fade-in">
                {error}
            </div>
          )}
        </div>

        {/* --- RESULTS DASHBOARD --- */}
        {report && (
          <div className="space-y-10 animate-fade-in-up">
            
            {/* 1. User Query Context (Visual Feedback) */}
            <div className="text-center">
                <div className="inline-block px-4 py-1 bg-slate-800 rounded-full text-xs text-slate-400 mb-2 border border-slate-700">
                    Analysis Request
                </div>
                <h3 className="text-xl md:text-2xl text-white font-medium">
                    "{report.reply && question ? question : `Analyze ${ticker} stock performance`}"
                </h3>
            </div>

            {/* 2. Charts & Data */}
            <section>
                <StockChart data={report.chart_data} />
            </section>

            {/* 3. The AI Report */}
            <section>
                <AnalysisCard report={report} />
            </section>
          </div>
        )}

        {/* --- LOADING SKELETON --- */}
        {loading && !report && (
            <div className="max-w-3xl mx-auto space-y-6 mt-12 opacity-50">
                <div className="h-96 w-full bg-slate-800/30 rounded-2xl animate-pulse"></div>
                <div className="h-40 w-full bg-slate-800/30 rounded-2xl animate-pulse"></div>
            </div>
        )}

      </div>
    </div>
  );
}

export default App;