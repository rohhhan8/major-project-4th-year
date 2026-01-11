// src/pages/QuizResultsPage.jsx
/**
 * Quiz Results Page - Enhanced Design
 * 
 * Features:
 * - 5-Pillar Diagnosis Breakdown
 * - Grid Layout for Video Recommendations (3x3)
 * - Improved AI Summary Card
 * - Better Thumbnail Handling
 */

import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
    CheckCircle, XCircle, PlayCircle, BarChart2, 
    ArrowRight, RefreshCcw, BookOpen, Target, Clock, Zap,
    Brain, Shield, Layout, Code, Search
} from 'lucide-react';

const QuizResultsPage = () => {
    const { state } = useLocation();
    const navigate = useNavigate();
    
    // Safety check
    if (!state || !state.results) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                    <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-gray-800 mb-4">No Results Found</h2>
                    <button 
                        onClick={() => navigate('/quiz/topics')}
                        className="px-6 py-3 bg-blue-500 text-white rounded-xl hover:bg-blue-600"
                    >
                        Take a Quiz
                    </button>
                </div>
            </div>
        );
    }

    const { 
        score, 
        total_questions, 
        percentage,
        passed, 
        diagnosis,
        recommendations 
    } = state.results;

    // Use all recommendations in a grid
    const videos = recommendations || [];

    const getThumbnail = (videoId) => {
        return `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`;  // Higher quality thumbnail
    };

    // Load more state - show 3 initially, then load more
    const [visibleCount, setVisibleCount] = useState(3);
    const visibleVideos = videos.slice(0, visibleCount);
    const hasMore = visibleCount < videos.length;

    const loadMore = () => {
        setVisibleCount(prev => Math.min(prev + 3, videos.length));
    };

    return (
        <div className="min-h-screen bg-gray-50 py-10 px-4">
            <div className="max-w-6xl mx-auto space-y-8">
                
                {/* 1. HEADER & SCORE */}
                <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="grid md:grid-cols-3 gap-6"
                >
                    {/* Score Card */}
                    <div className="bg-white rounded-2xl shadow-sm p-6 flex flex-col items-center justify-center text-center border border-gray-100">
                        <div className="relative mb-4">
                            <svg className="w-32 h-32 transform -rotate-90">
                                <circle cx="64" cy="64" r="56" stroke="#f3f4f6" strokeWidth="10" fill="transparent" />
                                <circle 
                                    cx="64" cy="64" r="56" 
                                    stroke={passed ? "#10b981" : "#f59e0b"} 
                                    strokeWidth="10" 
                                    fill="transparent" 
                                    strokeDasharray={352} 
                                    strokeDashoffset={352 - (352 * percentage) / 100} 
                                    strokeLinecap="round"
                                />
                            </svg>
                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                                <span className={`text-3xl font-bold ${passed ? "text-emerald-600" : "text-amber-500"}`}>
                                    {score}/{total_questions}
                                </span>
                            </div>
                        </div>
                        <h2 className="text-xl font-bold text-gray-800">{passed ? "Great Job!" : "Keep Learning!"}</h2>
                        <p className="text-sm text-gray-500 mt-1">{passed ? "Ready for the next level" : "Review the concepts below"}</p>
                    </div>

                    {/* AI Diagnosis Summary */}
                    <div className="md:col-span-2 bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl shadow-lg p-8 text-white relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-4 opacity-10">
                            <Brain size={120} />
                        </div>
                        <div className="relative z-10 h-full flex flex-col justify-between">
                            <div>
                                <div className="flex items-center gap-2 mb-4">
                                    <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
                                        <Brain size={20} className="text-white" />
                                    </div>
                                    <span className="font-bold text-blue-100 uppercase tracking-wider text-sm">AI Coach Insights</span>
                                </div>
                                <h3 className="text-2xl font-bold mb-3">{diagnosis.learner_profile.replace('_', ' ')} Profile</h3>
                                <p className="text-blue-50 text-lg leading-relaxed font-light">
                                    "{diagnosis.feedback || "Good effort! Focus on your weak areas to improve specific technical concepts."}"
                                </p>
                            </div>
                            
                            <div className="flex items-center gap-6 mt-6 pt-6 border-t border-white/10">
                                <div>
                                    <span className="text-blue-200 text-xs uppercase font-bold">Weakest Area</span>
                                    <div className="text-xl font-bold flex items-center gap-2 mt-1">
                                        <Target size={18} />
                                        {diagnosis.weakest_pillar}
                                    </div>
                                </div>
                                <div>
                                    <span className="text-blue-200 text-xs uppercase font-bold">Focus</span>
                                    <div className="text-xl font-bold flex items-center gap-2 mt-1">
                                        <Search size={18} />
                                        Concept Building
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </motion.div>

                {/* 2. PILLAR BREAKDOWN */}
                {diagnosis && (
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6"
                    >
                        <h3 className="text-lg font-bold text-gray-800 mb-6 flex items-center gap-2">
                            <BarChart2 className="text-blue-500" />
                            5-Pillar Performance Analysis
                        </h3>
                        
                        <div className="grid md:grid-cols-5 gap-4">
                            {diagnosis.pillar_breakdown && Object.entries(diagnosis.pillar_breakdown).map(([pillar, stats]) => (
                                <div key={pillar} className="bg-gray-50 rounded-xl p-4 border border-gray-100 text-center">
                                    <h4 className="font-bold text-gray-700 text-sm mb-2">{pillar}</h4>
                                    <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden mb-2">
                                        <div 
                                            className={`absolute top-0 left-0 h-full rounded-full transition-all duration-1000 ${
                                                stats.accuracy >= 80 ? 'bg-emerald-500' : 
                                                stats.accuracy >= 50 ? 'bg-amber-500' : 'bg-rose-500'
                                            }`}
                                            style={{ width: `${stats.accuracy}%` }}
                                        />
                                    </div>
                                    <div className="flex justify-between items-center text-xs text-gray-500 mt-2">
                                        <span>{stats.correct}/{stats.total}</span>
                                        {stats.rushed_count > 0 && (
                                            <span className="text-amber-500 flex items-center gap-1 font-medium" title="Rushed Answers">
                                                <Zap size={10} /> {stats.rushed_count}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </motion.div>
                )}

                {/* 3. VIDEO RECOMMENDATIONS GRID */}
                {videos.length > 0 && (
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                                <PlayCircle className="text-red-500" />
                                Recommended Learning Path
                            </h3>
                            <span className="text-sm text-gray-500 font-medium">
                                Showing {visibleVideos.length} of {videos.length} videos
                            </span>
                        </div>
                        
                        <div className="grid md:grid-cols-3 gap-6">
                            {visibleVideos.map((rec, idx) => (
                                <motion.div
                                    key={rec.video_id + idx}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.1 * (idx % 3) }}
                                    whileHover={{ y: -5 }}
                                    onClick={() => navigate(`/watch?id=${rec.video_id}&title=${encodeURIComponent(rec.title)}`)}
                                    className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden cursor-pointer group hover:shadow-lg transition-all"
                                >
                                    {/* Thumbnail */}
                                    <div className="relative aspect-video bg-gray-100">
                                        <img 
                                            src={rec.thumbnail || getThumbnail(rec.video_id)}
                                            alt={rec.title}
                                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                                            loading="lazy"
                                            onError={(e) => {
                                                // Fallback to different thumbnail quality
                                                const fallbacks = [
                                                    `https://i.ytimg.com/vi/${rec.video_id}/mqdefault.jpg`,
                                                    `https://i.ytimg.com/vi/${rec.video_id}/default.jpg`,
                                                    'https://via.placeholder.com/480x360?text=Video'
                                                ];
                                                const currentSrc = e.target.src;
                                                const nextFallback = fallbacks.find(f => !currentSrc.includes(f.split('/').pop()));
                                                if (nextFallback) e.target.src = nextFallback;
                                            }}
                                        />
                                        <div className="absolute inset-0 bg-black/20 group-hover:bg-black/10 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
                                            <div className="w-14 h-14 bg-white/90 rounded-full flex items-center justify-center backdrop-blur-sm shadow-lg">
                                                <PlayCircle className="w-8 h-8 text-red-600 ml-1" />
                                            </div>
                                        </div>
                                        {/* Relevance Badge */}
                                        <span className={`absolute top-2 left-2 px-2 py-1 text-xs font-bold rounded ${
                                            rec.relevance_percent >= 70 ? 'bg-green-500 text-white' :
                                            rec.relevance_percent >= 50 ? 'bg-yellow-500 text-white' :
                                            'bg-gray-500 text-white'
                                        }`}>
                                            {rec.relevance_percent?.toFixed(0) || Math.round(rec.score * 100)}% match
                                        </span>
                                    </div>
                                    
                                    {/* Content */}
                                    <div className="p-4">
                                        <h4 className="font-bold text-gray-900 line-clamp-2 mb-2 group-hover:text-primary transition-colors">
                                            {rec.title}
                                        </h4>
                                        <p className="text-xs text-gray-500 line-clamp-2 mb-3">
                                            {rec.description}
                                        </p>
                                        <div className="flex items-center justify-between mt-auto">
                                            <span className={`text-xs font-semibold ${
                                                rec.relevance_percent >= 70 ? 'text-green-600' :
                                                rec.relevance_percent >= 50 ? 'text-yellow-600' :
                                                'text-gray-500'
                                            }`}>
                                                {rec.difficulty || 'General'}
                                            </span>
                                            <button className="text-xs font-bold text-primary flex items-center gap-1 group-hover:underline">
                                                Watch <ArrowRight size={12} />
                                            </button>
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </div>

                        {/* Load More Button */}
                        {hasMore && (
                            <div className="flex justify-center mt-8">
                                <motion.button
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={loadMore}
                                    className="px-8 py-3 bg-white border-2 border-gray-200 text-gray-700 font-bold rounded-xl hover:border-primary hover:text-primary transition-all flex items-center gap-2 shadow-sm"
                                >
                                    Load More Videos
                                    <span className="text-sm text-gray-400">({videos.length - visibleCount} remaining)</span>
                                </motion.button>
                            </div>
                        )}
                    </motion.div>
                )}

                {/* 4. ACTIONS */}
                <div className="flex justify-center gap-4 pt-8">
                    <button
                        onClick={() => navigate('/quiz/topics')}
                        className="px-8 py-4 bg-white border-2 border-gray-200 text-gray-700 font-bold rounded-xl hover:border-blue-500 hover:text-blue-600 transition-all flex items-center gap-2"
                    >
                        <RefreshCcw size={20} />
                        Try Another Topic
                    </button>
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="px-8 py-4 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 shadow-lg shadow-blue-200 transition-all flex items-center gap-2"
                    >
                        <BarChart2 size={20} />
                        Go to Dashboard
                    </button>
                </div>
            </div>
        </div>
    );
};

export default QuizResultsPage;
