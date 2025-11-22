import React from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Line, ComposedChart 
} from 'recharts';

const StockChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 w-full bg-slate-800/50 rounded-xl border border-slate-700 flex items-center justify-center text-slate-400">
        <p>No chart data available yet.</p>
      </div>
    );
  }

  return (
    <div className="h-96 w-full bg-slate-900/80 backdrop-blur-md rounded-xl p-6 border border-slate-700 shadow-2xl">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-slate-200">Price Forecast (7-Day) & Confidence Interval</h3>
        <div className="flex items-center gap-4 text-xs hidden sm:flex">
            <div className="flex items-center gap-2">
                <span className="w-3 h-3 bg-emerald-500 rounded-full"></span>
                <span className="text-slate-400">Historical</span>
            </div>
            <div className="flex items-center gap-2">
                <span className="w-3 h-3 border border-blue-500 border-dashed bg-transparent rounded-full"></span>
                <span className="text-slate-400">Forecast</span>
            </div>
            <div className="flex items-center gap-2">
                <span className="w-3 h-3 bg-blue-500/30 rounded-full"></span>
                <span className="text-slate-400">90% Confidence Range</span>
            </div>
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height="85%">
        <ComposedChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
          <XAxis 
            dataKey="date" 
            stroke="#94a3b8" 
            tick={{fontSize: 12}} 
            tickMargin={10}
            tickFormatter={(str) => {
                const d = new Date(str);
                return `${d.getMonth()+1}/${d.getDate()}`;
            }}
          />
          <YAxis 
            domain={['auto', 'auto']} 
            stroke="#94a3b8" 
            tick={{fontSize: 12}} 
            tickFormatter={(val) => `$${val}`}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }}
            itemStyle={{ color: '#f8fafc' }}
            labelStyle={{ color: '#94a3b8', marginBottom: '0.5rem' }}
            labelFormatter={(label) => new Date(label).toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' })}
          />
          
          {/* Confidence Band */}
          <Area 
            type="monotone" 
            dataKey="upper" 
            stroke="none" 
            fill="url(#colorConfidence)" 
          />
          <Area 
            type="monotone" 
            dataKey="lower" 
            stroke="none" 
            fill="url(#colorConfidence)" 
          />

          {/* Price Lines */}
          <Line 
            type="monotone" 
            dataKey="price" 
            stroke="#10b981" 
            strokeWidth={3} 
            dot={false} 
            connectNulls={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default StockChart;