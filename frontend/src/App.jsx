// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import MainLayout from './MainLayout';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import DashboardPage from './pages/DashboardPage';
import VideoResultsPage from './pages/VideoResultsPage';
import QuizTopicsPage from './pages/QuizTopicsPage';
import QuizSubtopicsPage from './pages/QuizSubtopicsPage';
import QuizPage from './pages/QuizPage';
import QuizResultsPage from './pages/QuizResultsPage';
import VideoPlayerPage from './pages/VideoPlayerPage';
import VideoHistoryPage from './pages/VideoHistoryPage';
import NotesPage from './pages/NotesPage';
import './index.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        {/* Routes with the main navigation bar */}
        <Route element={<MainLayout />}>
          <Route path="/results" element={<VideoResultsPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/quiz/topics" element={<QuizTopicsPage />} />
          <Route path="/quiz/subject/:subjectId" element={<QuizSubtopicsPage />} />
          <Route path="/quiz/results" element={<QuizResultsPage />} />
          <Route path="/quiz/start/:topicId" element={<QuizPage />} />
          <Route path="/quiz/:topic" element={<QuizPage />} /> {/* Legacy */}
          <Route path="/watch" element={<VideoPlayerPage />} />
          <Route path="/video" element={<VideoPlayerPage />} />
          <Route path="/videos" element={<VideoHistoryPage />} />
          <Route path="/notes" element={<NotesPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
