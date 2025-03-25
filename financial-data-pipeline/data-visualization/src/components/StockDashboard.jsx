import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import "chart.js/auto";

const tickers = [
  "AAPL",
  "GOOGL",
  "AMZN",
  "MSFT",
  "TSLA",
  "NVDA",
  "META",
  "NFLX",
  "SPY",
  "AMD",
  "INTC",
  "BA",
  "DIS",
  "PYPL",
  "SNAP",
  "TSM",
  "V",
  "MA",
  "VZ",
  "WMT",
  "PG",
  "KO",
  "PEP",
  "MCD",
  "BABA",
  "ORCL",
  "GE",
  "LMT",
  "CSCO",
  "IBM",
  "AMAT",
  "CAT",
  "CVX",
  "XOM",
  "GM",
  "F",
  "T",
];

const API_BASE_URL = "http://localhost:8081/api";

const StockDashboard = () => {
  const [selectedTicker, setSelectedTicker] = useState("AAPL");
  const [priceData, setPriceData] = useState(null);
  const [historicalData, setHistoricalData] = useState(null);
  const [companyInfo, setCompanyInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [predictions, setPredictions] = useState([]);

  useEffect(() => {
    fetchAllData(selectedTicker);
  }, [selectedTicker]);

  const fetchAllData = async (ticker) => {
    setLoading(true);
    setError(null);
    try {
      const [
        priceResponse,
        historicalResponse,
        infoResponse,
        predictionResponse,
      ] = await Promise.all([
        fetch(`${API_BASE_URL}/price?ticker=${ticker}`),
        fetch(
          `${API_BASE_URL}/historical?ticker=${ticker}&period=12mo&interval=1d`
        ),
        fetch(`${API_BASE_URL}/info?ticker=${ticker}`),
        fetch(`${API_BASE_URL}/predict?ticker=${ticker}&days=5`),
      ]);

      if (
        !priceResponse.ok ||
        !historicalResponse.ok ||
        !infoResponse.ok ||
        !predictionResponse.ok
      ) {
        throw new Error("Failed to fetch data");
      }

      const [priceData, historicalData, infoData, predictionData] =
        await Promise.all([
          priceResponse.json(),
          historicalResponse.json(),
          infoResponse.json(),
          predictionResponse.json(),
        ]);

      setPriceData(priceData);
      setHistoricalData(historicalData);
      setCompanyInfo(infoData);
      setPredictions(predictionData.predictions);
    } catch (error) {
      console.error("Error fetching data:", error);
      setError("Failed to fetch data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: priceData?.currency || "USD",
    }).format(value);
  };

  const formatVolume = (volume) => {
    if (volume >= 1e6) {
      return `${(volume / 1e6).toFixed(2)}M`;
    }
    if (volume >= 1e3) {
      return `${(volume / 1e3).toFixed(2)}K`;
    }
    return volume;
  };

  const chartData = historicalData
    ? {
        labels: historicalData.data.map((item) => item.Date.split(" ")[0]),
        datasets: [
          {
            label: `${historicalData.ticker} Price`,
            data: historicalData.data.map((item) => item.Close),
            borderColor: "rgb(75, 192, 192)",
            tension: 0.1,
            fill: false,
          },
        ],
      }
    : {};

  if (loading) {
    return (
      <div className="container">
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  if (!priceData || !historicalData || !companyInfo) {
    return null;
  }

  const { ticker, price, currency, change, change_percent } = priceData;
  const changeText = `${change.toFixed(2)} (${change_percent.toFixed(2)}%)`;
  const marketCap = companyInfo.market_cap
    ? `$${(companyInfo.market_cap / 1e9).toFixed(2)} billion`
    : "N/A";
  const employees = companyInfo.employees
    ? companyInfo.employees.toLocaleString()
    : "N/A";

  return (
    <div className="container">
      <h1>Stock Data Dashboard</h1>

      <div className="search-container">
        <select
          value={selectedTicker}
          onChange={(e) => setSelectedTicker(e.target.value)}
          disabled={loading}
        >
          {tickers.map((ticker) => (
            <option key={ticker} value={ticker}>
              {ticker}
            </option>
          ))}
        </select>
      </div>

      <div className="data-container">
        <div className="price-card">
          <h2>{ticker}</h2>
          <div className="price">{`${price.toFixed(2)} ${currency}`}</div>
          <div className={`change ${change >= 0 ? "positive" : "negative"}`}>
            {change >= 0 ? "▲" : "▼"} {changeText}
          </div>
        </div>

        <div className="chart-container">
          <h3>Price Chart (Last 30 Days)</h3>
          <Line
            data={chartData}
            options={{ responsive: true, maintainAspectRatio: true }}
          />
        </div>

        <div className="historical-table-container">
          <h3>Historical Data</h3>
          <div className="table-responsive">
            <table className="historical-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Open</th>
                  <th>High</th>
                  <th>Low</th>
                  <th>Close</th>
                  <th>Change</th>
                  <th>Volume</th>
                </tr>
              </thead>
              <tbody>
                {historicalData.data.map((item, index) => {
                  const change = item.Close - item.Open;
                  const changePercent = (change / item.Open) * 100;
                  return (
                    <tr key={index}>
                      <td>{formatDate(item.Date)}</td>
                      <td>{formatCurrency(item.Open)}</td>
                      <td>{formatCurrency(item.High)}</td>
                      <td>{formatCurrency(item.Low)}</td>
                      <td>{formatCurrency(item.Close)}</td>
                      <td className={change >= 0 ? "positive" : "negative"}>
                        {change >= 0 ? "▲" : "▼"}{" "}
                        {formatCurrency(Math.abs(change))} (
                        {changePercent.toFixed(2)}%)
                      </td>
                      <td>{formatVolume(item.Volume)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        <div className="info-container">
          <h3>Company Information</h3>
          <div className="info-grid">
            <div className="info-item">
              <strong>Name:</strong> {companyInfo.name || "N/A"}
            </div>
            <div className="info-item">
              <strong>Sector:</strong> {companyInfo.sector || "N/A"}
            </div>
            <div className="info-item">
              <strong>Industry:</strong> {companyInfo.industry || "N/A"}
            </div>
            <div className="info-item">
              <strong>Country:</strong> {companyInfo.country || "N/A"}
            </div>
            <div className="info-item">
              <strong>Market Cap:</strong> {marketCap}
            </div>
            <div className="info-item">
              <strong>Employees:</strong> {employees}
            </div>
            <div className="info-item">
              <strong>Website:</strong>{" "}
              {companyInfo.website ? (
                <a
                  href={companyInfo.website}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {companyInfo.website}
                </a>
              ) : (
                "N/A"
              )}
            </div>
          </div>
          <div className="description">
            <strong>Description:</strong>{" "}
            {companyInfo.description || "No description available."}
          </div>
        </div>
      </div>
      <div className="prediction-container">
        <h3>Future Predictions (Next 5 Days)</h3>
        <table className="prediction-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Predicted Close Price</th>
            </tr>
          </thead>
          <tbody>
            {predictions.map((prediction, index) => (
              <tr key={index}>
                <td>{prediction.date}</td>
                <td>${prediction.predicted_close.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default StockDashboard;
