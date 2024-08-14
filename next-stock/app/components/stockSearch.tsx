"use client";

import React, { useState } from "react";
import CandlestickChart from "../components/stockChart";

export default function StockSearch() {
  const [symbol, setSymbol] = useState<string>("");
  const [stockData, setStockData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("access_token");

      const response = await fetch(
        `http://localhost:8000/stocks/search/${symbol}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Stock not found or an error occurred.");
      }

      const data = await response.json();
      setStockData(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="text"
        value={symbol}
        onChange={(e) => setSymbol(e.target.value)}
        placeholder="Enter stock symbol"
      />
      <button onClick={handleSearch}>Search</button>

      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}
      {stockData && (
        <div>
          <CandlestickChart symbol={stockData.symbol} />
        </div>
      )}
    </div>
  );
}
