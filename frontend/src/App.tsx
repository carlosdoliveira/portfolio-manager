import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "./components/layout/Layout";

import Dashboard from "./pages/Dashboard";
import Import from "./pages/Import";
import Portfolio from "./pages/Portfolio";
import AssetDetail from "./pages/AssetDetail";
import Analysis from "./pages/Analysis";
import Settings from "./pages/Settings";

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/import" element={<Import />} />
          <Route path="/portfolio" element={<Portfolio />} />
          <Route path="/portfolio/:id" element={<AssetDetail />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
