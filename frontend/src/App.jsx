import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Predict from './pages/Predict';
import Dashboard from './pages/Dashboard';
import './App.css';

export default function App() {
  const [history, setHistory] = useState([]);

  function addPrediction(entry) {
    setHistory(prev => [...prev, entry]);
  }

  return (
    <BrowserRouter>
      <div className="app-shell">
        <Header />
        <Routes>
          <Route path="/"          element={<Predict   onNewPrediction={addPrediction} />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}