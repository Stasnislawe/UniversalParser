import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import AnalysisPage from "./pages/AnalysisPage";
import FieldsPage from "./pages/FieldsPage";
import ConfigsPage from "./pages/ConfigsPage";
import ScrapePage from "./pages/ScrapePage";
import ResultsPage from "./pages/ResultsPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/analysis/:taskId" element={<AnalysisPage />} />
        <Route path="/fields/:sessionId" element={<FieldsPage />} />
        <Route path="/configs" element={<ConfigsPage />} />
        <Route path="/scrape/:configId?" element={<ScrapePage />} />
        <Route path="/results/:taskId" element={<ResultsPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;