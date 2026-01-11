// src/pages/QuizPage.jsx
/**
 * Quiz Page - Interactive quiz with per-question timing
 * 
 * Uses the new Two-Collection System:
 * - GET /quiz/start/{topic_id} to fetch random questions
 * - POST /quiz/submit with topic_id and per-question timing
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, CheckCircle, XCircle, Loader2, ArrowLeft, Clock } from 'lucide-react';
import axios from 'axios';

// Timer Component
const TimerDisplay = ({ startTime }) => {
    const [elapsed, setElapsed] = useState(0);

    useEffect(() => {
        if (!startTime) return;
        const interval = setInterval(() => {
            setElapsed(Math.floor((Date.now() - startTime) / 1000));
        }, 1000);
        return () => clearInterval(interval);
    }, [startTime]);

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
    };

    return <span className="font-mono text-lg">{formatTime(elapsed)}</span>;
};

const QuizPage = () => {
    const { topicId, topic } = useParams(); // Support both new and legacy routes
    const navigate = useNavigate();
    
    const [quiz, setQuiz] = useState(null);
    const [answers, setAnswers] = useState({}); // { questionId: {option_id, time_taken} }
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [error, setError] = useState(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    
    // Time Tracking
    const [quizStartTime, setQuizStartTime] = useState(null);
    const [questionStartTime, setQuestionStartTime] = useState(null);

    // Resolve topic ID from URL params
    const resolvedTopicId = topicId || topic;

    useEffect(() => {
        const fetchQuiz = async () => {
            try {
                console.log('[QuizPage] Fetching quiz for:', resolvedTopicId);
                
                // Determine which endpoint to use
                const endpoint = topicId 
                    ? `http://localhost:8000/quiz/start/${topicId}`
                    : `http://localhost:8000/quiz/legacy/${topic}`;
                
                const response = await axios.get(endpoint, { withCredentials: true });
                console.log('[QuizPage] Quiz loaded:', response.data);
                
                setQuiz(response.data);
                
                // Initialize timer
                const now = Date.now();
                setQuizStartTime(now);
                setQuestionStartTime(now);
            } catch (err) {
                console.error('[QuizPage] Error:', err);
                setError('Failed to load the quiz. Please try again.');
            }
        };
        
        if (resolvedTopicId) {
            fetchQuiz();
        }
    }, [resolvedTopicId, topicId, topic]);

    // Track question time when navigating
    useEffect(() => {
        if (quiz && quiz.questions) {
            setQuestionStartTime(Date.now());
        }
    }, [currentQuestionIndex, quiz]);

    const handleOptionSelect = (questionId, optionId) => {
        const timeSpent = Math.round((Date.now() - questionStartTime) / 1000);
        
        setAnswers(prev => ({
            ...prev,
            [questionId]: {
                selected_option_id: optionId,
                time_taken_seconds: timeSpent
            }
        }));
    };

    const handleNext = () => {
        if (currentQuestionIndex < quiz.questions.length - 1) {
            setCurrentQuestionIndex(prev => prev + 1);
        }
    };

    const handlePrev = () => {
        if (currentQuestionIndex > 0) {
            setCurrentQuestionIndex(prev => prev - 1);
        }
    };

    const handleSubmit = async () => {
        setIsSubmitting(true);
        
        const totalTime = Math.round((Date.now() - quizStartTime) / 1000);
        
        // Build submission in new format
        const formattedAnswers = Object.entries(answers).map(([questionId, data]) => ({
            question_id: questionId,
            selected_option_id: data.selected_option_id,
            time_taken_seconds: data.time_taken_seconds
        }));

        const submission = {
            topic_id: quiz.topic_id || resolvedTopicId,
            answers: formattedAnswers,
            total_time_seconds: totalTime
        };
        
        console.log('[QuizPage] Submitting:', submission);

        try {
            const response = await axios.post('http://localhost:8000/quiz/submit', submission, {
                withCredentials: true
            });
            
            console.log('[QuizPage] Result:', response.data);
            
            navigate('/quiz/results', { 
                state: { 
                    results: response.data,
                    topic: quiz.topic_name || quiz.topic || resolvedTopicId
                }
            });
        } catch (err) {
            console.error('[QuizPage] Submit error:', err);
            setError('Failed to submit the quiz.');
        } finally {
            setIsSubmitting(false);
        }
    };

    // Loading State
    if (!quiz && !error) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <motion.div 
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex flex-col items-center gap-4"
                >
                    <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
                    <p className="text-gray-600 font-medium">Loading Quiz...</p>
                </motion.div>
            </div>
        );
    }

    // Error State
    if (error) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
                <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white p-8 rounded-2xl shadow-lg max-w-md text-center"
                >
                    <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                    <h2 className="text-xl font-bold text-gray-900 mb-2">Oops!</h2>
                    <p className="text-gray-600 mb-6">{error}</p>
                    <button 
                        onClick={() => navigate('/quiz/topics')}
                        className="px-6 py-3 bg-blue-500 text-white font-bold rounded-xl hover:bg-blue-600 transition-colors"
                    >
                        Back to Topics
                    </button>
                </motion.div>
            </div>
        );
    }

    const currentQuestion = quiz.questions[currentQuestionIndex];
    const currentAnswer = answers[currentQuestion.id];
    const progress = ((currentQuestionIndex + 1) / quiz.questions.length) * 100;
    const answeredCount = Object.keys(answers).length;

    return (
        <div className="min-h-screen bg-gray-50 py-8 px-4">
            {/* Header */}
            <div className="max-w-3xl mx-auto mb-6">
                <div className="flex justify-between items-center mb-4">
                    <button 
                        onClick={() => navigate('/quiz/topics')}
                        className="flex items-center gap-2 text-gray-600 hover:text-gray-900 font-medium"
                    >
                        <ArrowLeft size={20} />
                        Back to Topics
                    </button>
                    
                    <div className="flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-full font-bold">
                        <Clock size={18} />
                        <TimerDisplay startTime={quizStartTime} />
                    </div>
                </div>
                
                {/* Progress Bar */}
                <div className="bg-white rounded-xl p-4 shadow-sm">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-bold text-gray-700">
                            Question {currentQuestionIndex + 1} of {quiz.questions.length}
                        </span>
                        <span className="text-sm font-medium text-blue-600">
                            {answeredCount} answered
                        </span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <motion.div 
                            className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
                            animate={{ width: `${progress}%` }}
                        />
                    </div>
                </div>
            </div>

            {/* Quiz Card */}
            <motion.div className="max-w-3xl mx-auto">
                <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
                    {/* Topic Header */}
                    <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-8 py-6">
                        <span className="inline-block px-3 py-1 bg-white/20 rounded-full text-white text-sm font-medium mb-2">
                            {currentQuestion.difficulty || 'Medium'} • {currentQuestion.diagnosis_pillar}
                        </span>
                        <h1 className="text-2xl font-bold text-white">
                            {quiz.topic_name || quiz.topic}
                        </h1>
                    </div>

                    {/* Question */}
                    <div className="p-8">
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={currentQuestionIndex}
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                            >
                                <h2 className="text-xl font-bold text-gray-900 mb-8 leading-relaxed">
                                    {currentQuestion.question_text}
                                </h2>

                                {/* Options */}
                                <div className="space-y-3">
                                    {currentQuestion.options.map((option, index) => {
                                        const isSelected = currentAnswer?.selected_option_id === option.id;
                                        const optionLetter = option.id || String.fromCharCode(65 + index);
                                        
                                        return (
                                            <motion.button
                                                key={option.id}
                                                onClick={() => handleOptionSelect(currentQuestion.id, option.id)}
                                                whileHover={{ scale: 1.01 }}
                                                whileTap={{ scale: 0.99 }}
                                                className={`
                                                    w-full text-left p-4 rounded-xl border-2 transition-all flex items-center gap-4
                                                    ${isSelected 
                                                        ? 'bg-blue-50 border-blue-500' 
                                                        : 'bg-gray-50 border-gray-200 hover:border-blue-300'
                                                    }
                                                `}
                                            >
                                                <span className={`
                                                    w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg
                                                    ${isSelected ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-600'}
                                                `}>
                                                    {optionLetter}
                                                </span>
                                                <span className={`flex-1 font-medium ${isSelected ? 'text-blue-900' : 'text-gray-700'}`}>
                                                    {option.text}
                                                </span>
                                                {isSelected && <CheckCircle className="w-6 h-6 text-blue-500" />}
                                            </motion.button>
                                        );
                                    })}
                                </div>

                                {/* Ideal Time Indicator */}
                                <div className="mt-4 text-sm text-gray-400 text-right">
                                    Ideal time: {currentQuestion.ideal_time_seconds}s
                                </div>
                            </motion.div>
                        </AnimatePresence>
                    </div>

                    {/* Navigation */}
                    <div className="px-8 py-6 bg-gray-50 border-t flex justify-between items-center">
                        <button
                            onClick={handlePrev}
                            disabled={currentQuestionIndex === 0}
                            className={`
                                px-6 py-3 rounded-xl font-bold transition-all
                                ${currentQuestionIndex === 0 
                                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
                                    : 'bg-white border-2 border-gray-200 text-gray-700 hover:border-blue-500'
                                }
                            `}
                        >
                            Previous
                        </button>

                        {currentQuestionIndex < quiz.questions.length - 1 ? (
                            <button 
                                onClick={handleNext}
                                className="px-6 py-3 bg-blue-500 text-white font-bold rounded-xl hover:bg-blue-600 flex items-center gap-2"
                            >
                                Next
                                <ChevronRight size={20} />
                            </button>
                        ) : (
                            <button 
                                onClick={handleSubmit}
                                disabled={isSubmitting || answeredCount < quiz.questions.length}
                                className={`
                                    px-8 py-3 font-bold rounded-xl flex items-center gap-2
                                    ${answeredCount < quiz.questions.length
                                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                        : 'bg-blue-500 text-white hover:bg-blue-600'
                                    }
                                `}
                            >
                                {isSubmitting ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        Submitting...
                                    </>
                                ) : (
                                    <>
                                        Submit Quiz
                                        <CheckCircle size={20} />
                                    </>
                                )}
                            </button>
                        )}
                    </div>
                </div>

                {/* Question Navigator */}
                <div className="mt-6 bg-white rounded-xl p-4 shadow-sm">
                    <p className="text-sm font-medium text-gray-600 mb-3">Jump to question:</p>
                    <div className="flex flex-wrap gap-2">
                        {quiz.questions.map((q, index) => {
                            const isAnswered = answers[q.id] !== undefined;
                            const isCurrent = index === currentQuestionIndex;
                            
                            return (
                                <button
                                    key={q.id}
                                    onClick={() => setCurrentQuestionIndex(index)}
                                    className={`
                                        w-10 h-10 rounded-lg font-bold transition-all
                                        ${isCurrent 
                                            ? 'bg-blue-500 text-white' 
                                            : isAnswered 
                                                ? 'bg-blue-100 text-blue-700' 
                                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                        }
                                    `}
                                >
                                    {index + 1}
                                </button>
                            );
                        })}
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default QuizPage;
