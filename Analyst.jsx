import React, { useState } from "react";
import Header from "../Components/Header";
import Plot from 'react-plotly.js';
import ReactMarkdown from 'react-markdown';


const PortfolioSummary = () => {
  const [mode, setMode] = useState("single_stock"); // or "single_stock"
  const [ticker, setTicker] = useState("");
  
  const [startDate, setStartDate] = useState("2025-01-03");
  const [endDate, setEndDate] = useState(() => {
    const today = new Date();
    return today.toISOString().split("T")[0]; // formats to 'YYYY-MM-DD'
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const [showVisionChart, setShowVisionChart] = useState(false);
  const [visionChartJson, setVisionChartJson] = useState(null);
  const [visionChartAnalysis, setVisionChartAnalysis] = useState(null);

  const [showSummary, setShowSummary] = useState(false);
  const [showNews, setShowNews] = useState(false);
  const [showRiskMetrics, setShowRiskMetrics] = useState(false);

  const [riskSummary, setRiskSummary] = useState("");
  const [summarizingRisk, setSummarizingRisk] = useState(false);


  const fetchVisionChart = async () => {
    try {
      console.log("Fetching Vision Chart for:", ticker);
      const res = await fetch("http://localhost:8000/vision_model_analysis/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tickers: [ticker],
          start_date: startDate,
          end_date: endDate,
          indicators: ["20-Day SMA", "VWAP", "20-Day EMA", "20-Day Bollinger Bands"]
        })
      });
      const data = await res.json();
      console.log("Vision Chart data:", data);

      if (data.results && data.results.length > 0) {
        const chartJson = data.results[0].chart_json;
        setVisionChartJson(JSON.parse(chartJson));
        setVisionChartAnalysis(data.results[0].analysis);
      }
    } catch (err) {
      console.error("Failed to load vision chart", err);
    }
  };

  const runAnalysis = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch("http://localhost:8000/comprehensive_summary/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: parseInt(localStorage.getItem("userID") || "1"),
          mode: "single_stock", 
          ticker,
          start_date: startDate,
          end_date: endDate
        })
      });
      const data = await res.json();
      console.log("Comprehensive Summary result:", data);
      setResult(data);
    } catch (err) {
      console.error("Error running summary:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 overflow-auto relative z-10">
      <Header title="Comprehensive Analyst Summary" />

      <main className="max-w-7xl mx-auto py-6 px-4 lg:px-8 space-y-6">

        {/* Mode toggle */}
        <div className="bg-gray-800 p-4 rounded space-y-4">
          <h2 className="text-xl font-bold">Configuration</h2>

          

          {mode === "single_stock" && (
            <div>
              <label className="block font-semibold">Ticker</label>
              <input
                type="text"
                value={ticker}
                onChange={e => setTicker(e.target.value.toUpperCase())}
                placeholder="AAPL"
                className="text-black p-2 rounded w-full"
              />
            </div>
          )}

          <div className="flex space-x-4 mt-4">
            <div>
              <label>Start Date</label>
              <input
                type="date"
                value={startDate}
                onChange={e => setStartDate(e.target.value)}
                className="text-black p-2 rounded"
              />
            </div>
            <div>
              <label>End Date</label>
              <input
                type="date"
                value={endDate}
                onChange={e => setEndDate(e.target.value)}
                className="text-black p-2 rounded"
              />
            </div>
          </div>

          <button
            onClick={runAnalysis}
            className="mt-4 bg-green-600 px-4 py-2 rounded hover:bg-green-700"
          >
            {loading ? "Running..." : "Run Analysis"}
          </button>
        </div>

        {/* Stock Summary */}
        <div className="bg-gray-800 p-4 rounded shadow mt-4">
          <button
            onClick={() => setShowSummary(!showSummary)}
            className="bg-purple-600 px-4 py-2 rounded hover:bg-purple-700 transition mb-2"
          >
            {showSummary ? "Hide 📝 Stock Summary" : "Show 📝 Stock Summary"}
          </button>

          {showSummary && result?.stock_summary && (
            <div className="prose prose-invert max-w-none text-sm text-gray-200">
              <ReactMarkdown>{result.stock_summary.summary}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Vision Chart */}
        <div className="bg-gray-800 p-4 rounded shadow">
          <button
            onClick={() => {
              if (!showVisionChart) fetchVisionChart();
              setShowVisionChart(!showVisionChart);
            }}
            className="bg-blue-600 px-4 py-2 rounded hover:bg-blue-700 transition mb-2"
            disabled={!ticker}
          >
            {showVisionChart ? "Hide 📈 Vision Chart" : "Show 📈 Vision Chart"}
          </button>



          {showVisionChart && visionChartJson && (
            <>
              <Plot
                key={`vision-chart-${ticker}-${startDate}-${endDate}-${visionChartJson.data.length}`}
                data={visionChartJson.data}
                layout={{
                  ...visionChartJson.layout,
                  width: 800,
                  height: 400,
                  autosize: true
                }}
                style={{ width: "100%", height: "auto" }}
              />


              <hr className="my-4 border-gray-600" />

              {/* Now the text below the chart */}
              {visionChartAnalysis && (
                <div className="mt-4 space-y-2 text-gray-200">
                  <div>
                    <span className="font-bold text-blue-400">Action:</span> {visionChartAnalysis.action || "N/A"}
                  </div>
                  <div>
                    <span className="font-bold text-blue-400">Justification:</span> {visionChartAnalysis.justification || "N/A"}
                  </div>
                  <div>
                    <span className="font-bold text-blue-400">Recommendation:</span> {visionChartAnalysis.recommendations || "N/A"}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        

       {/* News Sentiment */}
        <div className="bg-gray-800 p-4 rounded shadow mt-4">
          <button
            onClick={() => setShowNews(!showNews)}
            className="bg-green-600 px-4 py-2 rounded hover:bg-green-700 transition mb-2"
          >
            {showNews ? "Hide 📰 News Sentiment" : "Show 📰 News Sentiment"}
          </button>

          {showNews && result?.news_sentiment && (
            <div className="bg-gray-800 p-4 rounded shadow">
              <h2 className="text-lg font-bold mb-2">Results for {result.news_sentiment.ticker}</h2>
              <p className="mb-2">
                🧠 <strong>Average VADER Score:</strong> {result.news_sentiment.average_score}
              </p>
              <p className="mb-4">
                📊 <strong>LLM Sentiment Breakdown:</strong>{" "}
                🟢 Positive: {result.news_sentiment.sentiment_breakdown.Positive || 0},{" "}
                ⚪ Neutral: {result.news_sentiment.sentiment_breakdown.Neutral || 0},{" "}
                🔴 Negative: {result.news_sentiment.sentiment_breakdown.Negative || 0}
              </p>
              {result.news_sentiment.summary && (
                <div className="bg-gray-700 p-4 rounded mb-4">
                  <h3 className="text-md font-bold text-indigo-400 mb-2">🧾 Market Summary:</h3>
                  <div className="text-lg text-gray-200 whitespace-pre-wrap">
                    <ReactMarkdown>{result.news_sentiment.summary}</ReactMarkdown>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>


        {/* Risk Metrics */}
        <div className="bg-gray-800 p-4 rounded shadow mt-4">
          <button
            onClick={async () => {
              if (!showRiskMetrics) {
                setSummarizingRisk(true);
                setRiskSummary("");
                try {
                  const res = await fetch("http://localhost:8000/summarize_risk_metrics/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                      risk_metrics: {
                          volume_text: result?.stock_ai?.volume ?? "",
                          volatility_text: result?.stock_ai?.volatility_sharpe ?? "",
                          market_cap_text: result?.stock_ai?.basic_info ?? ""
                      }
                    })
                  });
                  const data = await res.json();
                  setRiskSummary(data.summary || "Failed to generate summary.");
                } catch (err) {
                  console.error("Error summarizing risk metrics:", err);
                  setRiskSummary("Error summarizing risk metrics.");
                } finally {
                  setSummarizingRisk(false);
                }
              }
              setShowRiskMetrics(!showRiskMetrics);
            }}
            className="bg-yellow-600 px-4 py-2 rounded hover:bg-yellow-700 transition mb-2"
            disabled={!result?.stock_ai}
          >
            {showRiskMetrics ? "Hide 📊 Risk Metrics Summary" : "Show 📊 Risk Metrics Summary"}
          </button>

          {showRiskMetrics && (
            <div className="mt-4 bg-gray-700 p-4 rounded text-gray-200">
              {summarizingRisk ? (
                <p>🔄 Summarizing risk metrics...</p>
              ) : (
                <>
                  <h3 className="text-md font-bold text-indigo-400 mb-2">📋 LLM Risk Summary:</h3>
                  <ReactMarkdown>{riskSummary}</ReactMarkdown>
                </>
              )}
            </div>
          )}
        </div>


        {/* Results display */}
        {result && (
          <div className="bg-gray-800 p-6 rounded shadow space-y-4 mt-8">
            <h2 className="text-xl font-bold">Results</h2>
            <pre className="whitespace-pre-wrap text-sm text-gray-200">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}

      </main>
    </div>
  );
};

export default PortfolioSummary;
