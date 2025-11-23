// src/pages/LandingPage.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const LandingPage = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const navigate = useNavigate();

    const handleSearch = (e) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            navigate(`/results?search_query=${encodeURIComponent(searchQuery)}`);
        }
    };

    const handleGoogleSignIn = () => {
        window.location.href = 'http://localhost:8000/auth/login';
    };

    return (
        <div className="min-h-screen bg-white flex flex-col">
            {/* Navigation */}
            <nav className="flex justify-between items-center px-8 py-4 border-b border-gray-200">
                <div className="flex items-center space-x-2">
                    <span className="text-2xl">🎓</span>
                    <h1 className="text-xl font-semibold text-gray-900">Study Buddy AI</h1>
                </div>
                <button
                    onClick={handleGoogleSignIn}
                    className="bg-gray-900 text-white px-6 py-2 rounded-md hover:bg-gray-800 transition-colors font-medium"
                >
                    Sign in with Google
                </button>
            </nav>

            {/* Main Content */}
            <main className="flex-1 flex items-center justify-center px-6 py-20">
                <div className="max-w-2xl w-full text-center">
                    <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight text-gray-900">
                        What do you want to learn today?
                    </h1>
                    <p className="text-lg text-gray-600 mb-12">
                        Discover personalized video content and AI-powered notes to master any topic
                    </p>

                    {/* Search Form */}
                    <form onSubmit={handleSearch} className="flex items-center bg-white border border-gray-300 rounded-lg shadow-sm hover:shadow-md transition-shadow">
                        {/* Search Icon */}
                        <svg
                            className="w-5 h-5 text-gray-400 ml-5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                            />
                        </svg>

                        {/* Input */}
                        <input
                            type="text"
                            placeholder="e.g. React Hooks, Machine Learning, Data Structures..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="flex-1 px-5 py-4 bg-transparent outline-none text-gray-700 placeholder-gray-500"
                        />

                        {/* Submit Button */}
                        <button
                            type="submit"
                            className="bg-gray-900 text-white font-medium px-8 py-4 hover:bg-gray-800 transition-colors"
                        >
                            Search
                        </button>
                    </form>
                </div>
            </main>
        </div>
    );
};

export default LandingPage;
