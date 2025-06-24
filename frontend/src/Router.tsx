import { BrowserRouter, Routes, Route } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import Home from "./pages/Home";
import Calculator from "./pages/Calculator";
import FreeRrifGuide from "./pages/FreeRrifGuide";

export default function Router() {
  return (
    <BrowserRouter basename="/">
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<Home />} />
          <Route path="calculator" element={<Calculator />} />
          <Route path="free-rrif-guide" element={<FreeRrifGuide />} />
          <Route path="*" element={<Home />} />  {/* fallback */}
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
