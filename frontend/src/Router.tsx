import { BrowserRouter, Routes, Route } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import Home from "./pages/Home";
import CalculatorPage from "./pages/CalculatorPage";
import FreeRrifGuidePage from "./pages/FreeRrifGuidePage";

export default function Router() {
  return (
    <BrowserRouter basename="/">
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<Home />} />
          <Route path="calculator" element={<CalculatorPage />} />
          <Route path="free-rrif-guide" element={<FreeRrifGuidePage />} />
          <Route path="*" element={<Home />} />  {/* fallback */}
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
