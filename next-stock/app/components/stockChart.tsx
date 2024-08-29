"use client";

import React, { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { ApexOptions } from "apexcharts";

// Dynamically import the chart to prevent SSR issues
const Chart = dynamic(() => import("react-apexcharts"), { ssr: false });

interface CandlestickChartProps {
  symbol: string;
}

export default function CandlestickChart({ symbol }: CandlestickChartProps) {
  const [stockData, setStockData] = useState<any>(null);
  const [series, setSeries] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStockData = async () => {
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
        const data = await response.json();

        if (!data.history) {
          throw new Error("Invalid data format received");
        }
        setStockData(data);

        const chartData = data.history.map((point: any) => {
          return {
            x: new Date(point.date).getTime(),
            y: [
              parseFloat(point.open.toFixed(2)),
              parseFloat(point.high.toFixed(2)),
              parseFloat(point.low.toFixed(2)),
              parseFloat(point.close.toFixed(2)),
            ],
          };
        });

        setSeries([{ data: chartData }]);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching stock data: ", error);
        setError("Error fetching stock data");
        setLoading(false);
      }
    };

    fetchStockData(); // Fetch initially

    const interval = setInterval(fetchStockData, 15000); // Fetch every 15 seconds

    return () => clearInterval(interval); // Cleanup on component unmount
  }, [symbol]);

  const options: ApexOptions = {
    chart: {
      type: "candlestick",
      height: 500,
      width: "100%",
    },
    title: {
      text: `${symbol} Stock Price`,
      align: "center",
    },
    xaxis: {
      type: "datetime",
    },
    yaxis: {
      tooltip: {
        enabled: true,
      },
    },
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <>
      <Chart
        options={options}
        series={series}
        type="candlestick"
        height={500}
        width="100%"
      />
      <div>
        {stockData && (
          <div>
            <h2>
              {stockData.name} ({stockData.symbol})
            </h2>
            <p>Current Price: ${stockData.current_price}</p>
          </div>
        )}
      </div>
    </>
  );
}
