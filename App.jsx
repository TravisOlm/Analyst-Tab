import { Route, Routes, Navigate, useLocation, BrowserRouter as Router } from 'react-router-dom';
import Login from './pages/LoginSignUp/LoginSignUp.jsx';
import Portfolio from "./pages/Portfolio"; 
import Chatbot from "./pages/Chatbot";
import AllStocks from "./pages/AllStocks" 
import Sidebar from './Components/Sidebar';
import React from 'react';
import InsertStocks from './pages/InsertStocks';
import VisionModel from './pages/VisionModel';
import NewsSentiment from './pages/NewsSentiment';
import Momentum from './pages/Momentum';
import Analyst from './pages/Analyst';
import PortfolioBreakdown from "./pages/PortfolioBreakdown";
import HeatmapTab from './pages/HeatmapTab.jsx';



function DashboardLayout() {
  const location = useLocation();
  const userId = localStorage.getItem('userID');

  // Optional: force redirect if user not logged in
  if (!userId) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className='flex h-screen bg-gray-900 text-gray-100 overflow-hidden'>
      {/* Background blur and gradient */}
      <div className='fixed inset-0 z-0'>
        <div className='absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 opacity-80' />
        <div className='absolute inset-0 backdrop-blur-sm' />
      </div>

      <Sidebar />
      <Routes>
        <Route path="/portfolio" element={<Portfolio />} />
        <Route path="/chatbot" element={<Chatbot />} />
        <Route path="/allstocks" element={<AllStocks />} />
        <Route path="/uploadportfolio" element={<InsertStocks />} />
        <Route path="/visionmodel" element={<VisionModel />} />
        <Route path="/news" element={<NewsSentiment />} />
        <Route path="/momentum" element={<Momentum />} />
        <Route path="/analyst" element={<Analyst />} />
        <Route path="/portfoliobreakdown" element={<PortfolioBreakdown />} />
        <Route path="/heatmap" element={<HeatmapTab />} />

        {/* fallback for any unknown path under /dashboard */}
        <Route path="*" element={<Navigate to="/portfolio" />} />

      </Routes>
    </div>
  );
}

export default function App() {
  return (
    
    <Routes>
      {/*  Default login route */}
      <Route path="/" element={<Login />} />
        
      {/* Protected dashboard layout */}
      <Route path="/*" element={<DashboardLayout />} />
    </Routes>
    
  );
}