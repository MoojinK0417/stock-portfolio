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
    <div className="flex flex-col items-end min-h-screen p-8">
      <div className="w-full flex justify-end mt-16">
        <div className="flex w-full max-w-md ml-auto">
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            placeholder="Enter stock symbol"
            className="flex-1 p-2 rounded border border-gray-300 rounded-r-md mr-2"
          />
          <button
            onClick={handleSearch}
            className="p-2 text-white rounded-r-md btn btn-outline btn-primary"
          >
            Search
          </button>
        </div>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}
      {stockData && (
        <div className="w-full flex justify-center mt-8">
          <div className="w-full max-w-8xl p-4 bg-white rounded shadow-md">
            <CandlestickChart symbol={stockData.symbol} />
          </div>
        </div>
      )}
    </div>
  );
}
