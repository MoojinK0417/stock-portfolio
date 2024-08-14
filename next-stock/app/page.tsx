import StockSearch from "./components/stockSearch";
import Navigation from "./components/navigation";
export default function Home() {
  return (
    <div>
      <div>
        <Navigation />
      </div>
      <div>
        <StockSearch />
      </div>
    </div>
  );
}
