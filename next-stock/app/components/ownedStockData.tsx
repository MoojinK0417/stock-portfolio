"use client";

import React, { useEffect, useState } from "react";

export default function OwnedStockData() {
  const [stockData, setStockData] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    const fetchOwnedStockData = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const userId = localStorage.getItem("user_id");

        const response = await fetch(
          `http://localhost:8000/portfolios/stocks/${userId}/current_prices/`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );
        const data = await response.json();

        if (!Array.isArray(data)) {
          throw new Error("Invalid data format received");
        }

        setStockData(data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching owned stock data: ", error);
        setError("Error fetching owned stock data");
        setLoading(false);
      }
    };

    fetchOwnedStockData();

    const interval = setInterval(fetchOwnedStockData, 15000); // Fetch every 15 seconds
    return () => clearInterval(interval); // Cleanup on component unmount
  }, []);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div className="flex justify-center mt-40">
      <div className="w-full max-w-4xl">
        <div className="overflow-x-auto bg-white shadow-md rounded-lg">
          <table className="table-auto w-full">
            {/* head */}
            <thead>
              <tr className="bg-gray-200">
                <th className="px-4 py-2">#</th>
                <th className="px-4 py-2">Name</th>
                <th className="px-4 py-2">Symbol</th>
                <th className="px-4 py-2">Quantity</th>
                <th className="px-4 py-2">Current Price</th>
                <th className="px-4 py-2">Average Price</th>
                <th className="px-4 py-2">Total Value</th>
                <th className="px-4 py-2">Profit</th>
              </tr>
            </thead>
            <tbody>
              {stockData.map((stock, index) => (
                <tr key={index} className="border-b">
                  <th className="px-4 py-2">{index + 1}</th>
                  <td className="px-4 py-2">{stock.name}</td>
                  <td className="px-4 py-2">{stock.symbol}</td>
                  <td className="px-4 py-2">{stock.quantity}</td>
                  <td className="px-4 py-2">${stock.current_price}</td>
                  <td className="px-4 py-2">${stock.average_price}</td>
                  <td className="px-4 py-2">${stock.total_value}</td>
                  <td
                    className={`px-4 py-2 ${
                      parseFloat(stock.profit) > 0
                        ? "text-green-500"
                        : "text-red-500"
                    }`}
                  >
                    ${stock.profit}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
