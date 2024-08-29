import StockSearch from "./components/stockSearch";
import Navigation from "./components/navigation";
import OwnedStockData from "./components/ownedStockData";
export default function Home() {
  return (
    <div>
      <div>
        <Navigation />
      </div>
      <div>
        <OwnedStockData />
      </div>
      <div>
        <StockSearch />
      </div>
    </div>
  );
}
