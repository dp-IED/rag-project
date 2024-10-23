import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { LandingPage } from "./LandingPage";
import { UploadPage } from "./Upload";
import { QueryPage } from "./Query";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/query" element={<QueryPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
