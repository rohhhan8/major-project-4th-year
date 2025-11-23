// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import MainLayout from './MainLayout';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import HomePage from './pages/HomePage'; // This will be used inside MainLayout
import VideoResultsPage from './pages/VideoResultsPage';
import QuizTopicsPage from './pages/QuizTopicsPage';
import QuizPage from './pages/QuizPage';
import VideoPlayerPage from './pages/VideoPlayerPage';
import NotesPage from './pages/NotesPage';
import './index.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        {/* Routes with the main navigation bar */}
        <Route element={<MainLayout />}>
          <Route path="/home" element={<HomePage />} />
          <Route path="/results" element={<VideoResultsPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/quiz/topics" element={<QuizTopicsPage />} />
          <Route path="/quiz/:topic" element={<QuizPage />} />
          <Route path="/watch" element={<VideoPlayerPage />} />
          <Route path="/notes" element={<NotesPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
