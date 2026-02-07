import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import TriagePage from './pages/TriagePage';
import RequestDetailsPage from './pages/RequestDetailsPage';
import ResourcesPage from './pages/ResourcesPage';
import Header from './components/Header';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/triage" element={<TriagePage />} />
            <Route path="/requests/:requestId" element={<RequestDetailsPage />} />
            <Route path="/resources" element={<ResourcesPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
