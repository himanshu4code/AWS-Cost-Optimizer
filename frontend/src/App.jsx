import React from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';

import Navigation from './components/Navigation';
import ConfigurationPage from './pages/ConfigurationPage';
import DashboardPage from './pages/DashboardPage';
import LandingPage from './pages/LandingPage';
import ReportsPage from './pages/ReportsPage';


function App({ apiBaseUrl }) {
  return (
    <BrowserRouter>
      <div className="shell">
        <div className="ambient ambient-a" />
        <div className="ambient ambient-b" />

        <Navigation />

        <main className="layout">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route
              path="/dashboard"
              element={<DashboardPage apiBaseUrl={apiBaseUrl} />}
            />
            <Route
              path="/configuration"
              element={<ConfigurationPage />}
            />
            <Route
              path="/reports"
              element={<ReportsPage />}
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
