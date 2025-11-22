import React from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, Activity, ShieldCheck, BrainCircuit } from 'lucide-react';

const AnalysisCard = ({ report }) => {
  let aiData = {};
  try {
    aiData = typeof report.reply === 'string' ? JSON.parse(report.reply) : report.reply;
  } catch (e) {
    console.error("JSON Parse Error", e);
    aiData = { analysis: "Error parsing analysis data.", confidence: "Low" };
  }

  const fundamentals = report.fundamentals || {};
  const trends = fundamentals.financial_trends || {};
  const isGrowing = trends.trend_direction === "Growing";

  return (
    <div className="space-y-6 animate-fade-in-up pb-12">
      
      {/* Executive Summary Header */}
      <div className="bg-slate-900/80 backdrop-blur-md border border-slate-700 rounded-2xl p-6 md:p-8 shadow-xl">
        <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4 mb-6">
            <div>
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                    <BrainCircuit className="text-purple-400" />
                    AI Executive Summary
                </h2>
                <p className="text-slate-400 text-sm mt-1">Synthesized from {report.sources?.length || 0} real-time news sources & market data</p>
            </div>
            <span className={`px-4 py-2 rounded-full text-sm font-bold border backdrop-blur-sm ${
                aiData.confidence === 'High' ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-400' : 
                aiData.confidence === 'Low' ? 'bg-rose-500/10 border-rose-500/50 text-rose-400' : 
                'bg-amber-500/10 border-amber-500/50 text-amber-400'
            }`}>
                {aiData.confidence || "Medium"} Confidence
            </span>
        </div>
        <p className="text-slate-300 leading-relaxed text-lg border-l-4 border-purple-500 pl-4">
            {aiData.analysis}
        </p>
      </div>

      {/* Key Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Fundamental Health */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:bg-slate-800/70 transition-colors">
            <h3 className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-4 flex items-center gap-2">
                <Activity size={14}/> Fundamental Health
            </h3>
            <div className="space-y-4">
                <div className="flex justify-between items-center">
                    <span className="text-slate-300">Quarterly Revenue</span>
                    <div className="text-right">
                        <div className="text-white font-mono font-medium">{trends.recent_quarterly_revenue?.[0] || "N/A"}</div>
                        <div className={`text-xs flex items-center justify-end gap-1 ${isGrowing ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {isGrowing ? <TrendingUp size={12}/> : <TrendingDown size={12}/>}
                            {trends.revenue_growth_last_q || "0%"}
                        </div>
                    </div>
                </div>
                <div className="w-full h-px bg-slate-700/50"></div>
                <div className="flex justify-between items-center">
                    <span className="text-slate-300">P/E Ratio</span>
                    <span className="text-white font-mono font-medium">{fundamentals.pe_ratio?.toFixed(2) || "N/A"}</span>
                </div>
                <div className="w-full h-px bg-slate-700/50"></div>
                <div className="flex justify-between items-center">
                    <span className="text-slate-300">Profit Margin</span>
                    <span className="text-white font-mono font-medium">{trends.recent_profit_margins?.[0] || "N/A"}</span>
                </div>
            </div>
        </div>

        {/* Technical Outlook */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:bg-slate-800/70 transition-colors">
             <h3 className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-4 flex items-center gap-2">
                <ShieldCheck size={14}/> Technical Outlook
            </h3>
            <div className="mb-4">
                <div className="text-slate-300 text-sm mb-2">{aiData.prediction_summary}</div>
            </div>
            <div className="bg-slate-900/80 rounded-lg p-4 border border-slate-600/50">
                <div className="flex justify-between items-end mb-1">
                    <span className="text-slate-400 text-sm">7-Day Target</span>
                    <span className="text-2xl font-bold text-white">${report.prediction?.forecast_7d}</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-500">90% Confidence Band</span>
                    <span className="text-slate-400 font-mono">
                        ${report.prediction?.forecast_range_low} - ${report.prediction?.forecast_range_high}
                    </span>
                </div>
            </div>
        </div>
      </div>

      {/* Risk Factors */}
      <div className="bg-rose-950/20 border border-rose-900/50 rounded-xl p-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-10">
            <AlertTriangle size={100} className="text-rose-500" />
        </div>
        <h3 className="text-rose-400 text-sm font-bold uppercase tracking-wider mb-3 flex items-center gap-2 relative z-10">
            <AlertTriangle size={16}/> Critical Risk Factors
        </h3>
        <p className="text-rose-200/90 leading-relaxed relative z-10">
            {aiData.risk_factors}
        </p>
      </div>

      {/* Sources Footer */}
      <div className="pt-6 border-t border-slate-800">
         <h4 className="text-xs font-semibold text-slate-500 uppercase mb-4">News Sources Analyzed</h4>
         <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {report.sources?.map((src, idx) => (
                <a key={idx} href={src.url} target="_blank" rel="noreferrer" className="block p-2 rounded bg-slate-800/50 hover:bg-slate-700 transition-colors text-xs text-slate-400 truncate border border-transparent hover:border-slate-600">
                    <span className="font-bold text-slate-300 mr-2">[{idx+1}]</span>
                    {src.title}
                </a>
            ))}
         </div>
      </div>
      
      <div className="text-center pt-8 text-xs text-slate-600">
        {aiData.disclaimer}
      </div>
    </div>
  );
};

export default AnalysisCard;