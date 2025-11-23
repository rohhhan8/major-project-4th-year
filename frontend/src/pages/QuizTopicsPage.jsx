// src/pages/QuizTopicsPage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const QuizTopicsPage = () => {
    const [topics, setTopics] = useState([]);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchTopics = async () => {
            try {
                // In a real app, the base URL would be in a config file
                const response = await axios.get('http://localhost:8000/quiz/topics');
                setTopics(response.data.topics);
            } catch (err) {
                setError('Failed to load quiz topics. Please try again later.');
                console.error(err);
            }
        };
        fetchTopics();
    }, []);

    const selectTopic = (topic) => {
        navigate(`/quiz/${encodeURIComponent(topic)}`);
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-4xl font-bold text-center mb-8">Choose a Quiz Topic</h1>
                {error && <p className="text-red-500 text-center">{error}</p>}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {topics.map((topic) => (
                        <div
                            key={topic}
                            onClick={() => selectTopic(topic)}
                            className="bg-white p-6 rounded-lg shadow-md cursor-pointer text-center transform hover:scale-105 transition-transform duration-300"
                        >
                            <h2 className="text-xl font-semibold">{topic}</h2>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default QuizTopicsPage;
