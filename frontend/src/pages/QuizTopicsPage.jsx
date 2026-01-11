// src/pages/QuizTopicsPage.jsx
/**
 * Quiz Topics Page - Subject Cards
 * 
 * Shows all SUBJECTS as cards. Clicking a subject navigates to subtopics page.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
    BookOpen, ArrowRight, AlertCircle,
    Code, Coffee, Globe, Atom, Server, Palette, Database, Network, Cpu, Terminal
} from 'lucide-react';
import axios from 'axios';

// Subject icons and colors mapping
const SUBJECT_CONFIG = {
    "topic_dsa": { icon: Code, color: "from-blue-500 to-blue-600", bgLight: "bg-blue-50", textColor: "text-blue-600" },
    "topic_java": { icon: Coffee, color: "from-orange-500 to-orange-600", bgLight: "bg-orange-50", textColor: "text-orange-600" },
    "topic_frontend": { icon: Globe, color: "from-purple-500 to-purple-600", bgLight: "bg-purple-50", textColor: "text-purple-600" },
    "topic_react": { icon: Atom, color: "from-cyan-500 to-cyan-600", bgLight: "bg-cyan-50", textColor: "text-cyan-600" },
    "topic_backend": { icon: Server, color: "from-green-500 to-green-600", bgLight: "bg-green-50", textColor: "text-green-600" },
    "topic_uiux": { icon: Palette, color: "from-pink-500 to-pink-600", bgLight: "bg-pink-50", textColor: "text-pink-600" },
    "topic_db": { icon: Database, color: "from-emerald-500 to-emerald-600", bgLight: "bg-emerald-50", textColor: "text-emerald-600" },
    "topic_cn": { icon: Network, color: "from-indigo-500 to-indigo-600", bgLight: "bg-indigo-50", textColor: "text-indigo-600" },
    "topic_os": { icon: Cpu, color: "from-red-500 to-red-600", bgLight: "bg-red-50", textColor: "text-red-600" },
    "topic_c": { icon: Terminal, color: "from-gray-600 to-gray-700", bgLight: "bg-gray-100", textColor: "text-gray-600" },
    // Node.js and Express
    "topic_nodejs": { icon: Server, color: "from-lime-500 to-green-600", bgLight: "bg-lime-50", textColor: "text-lime-600" },
    "topic_express": { icon: Server, color: "from-gray-700 to-gray-900", bgLight: "bg-gray-100", textColor: "text-gray-700" },
    "default": { icon: BookOpen, color: "from-slate-500 to-slate-600", bgLight: "bg-slate-50", textColor: "text-slate-600" }
};

const getSubjectConfig = (subjectId) => {
    return SUBJECT_CONFIG[subjectId] || SUBJECT_CONFIG["default"];
};

const QuizTopicsPage = () => {
    const [subjects, setSubjects] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchTopics = async () => {
            try {
                console.log('[QuizTopicsPage] Fetching subjects...');
                const response = await axios.get('http://localhost:8000/quiz/topics', {
                    withCredentials: true
                });
                console.log('[QuizTopicsPage] Response:', response.data);
                setSubjects(response.data.subjects || []);
            } catch (err) {
                console.error('[QuizTopicsPage] Error:', err);
                if (err.response?.status === 401) {
                    navigate('/login');
                } else {
                    setError('Failed to load quiz topics. Please check database connection.');
                }
            } finally {
                setLoading(false);
            }
        };
        fetchTopics();
    }, [navigate]);

    const openSubject = (subject) => {
        // Navigate to subtopics page with subject data
        navigate(`/quiz/subject/${subject._id}`, { state: { subject } });
    };

    // Loading State
    if (loading) {
        return (
            <div className="min-h-screen bg-white flex items-center justify-center">
                <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex flex-col items-center gap-4"
                >
                    <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                    <p className="text-gray-600 font-medium">Loading Subjects...</p>
                </motion.div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-white py-8 px-4">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <motion.div 
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-10"
                >
                    <h1 className="text-4xl font-extrabold text-gray-900 mb-3">
                        Choose Your <span className="text-primary">Subject</span>
                    </h1>
                    <p className="text-gray-500 max-w-xl mx-auto">
                        Select a subject to explore its topics and test your knowledge.
                    </p>
                </motion.div>

                {/* Error State */}
                {error && (
                    <motion.div 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-xl mb-8 flex items-center gap-3"
                    >
                        <AlertCircle className="w-5 h-5" />
                        {error}
                    </motion.div>
                )}

                {/* Subjects Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {subjects.map((subject, index) => {
                        const config = getSubjectConfig(subject._id);
                        const IconComponent = config.icon;
                        const topicCount = subject.topics?.length || 0;
                        
                        return (
                            <motion.button
                                key={subject._id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.05 }}
                                whileHover={{ y: -6, scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={() => openSubject(subject)}
                                className="bg-white rounded-2xl border border-gray-100 p-6 text-left hover:shadow-xl hover:border-primary/30 transition-all group relative overflow-hidden"
                            >
                                {/* Background decoration */}
                                <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${config.color} blur-3xl opacity-10 transform translate-x-10 -translate-y-10 group-hover:opacity-20 transition-opacity`}></div>
                                
                                {/* Icon */}
                                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${config.color} flex items-center justify-center shadow-lg mb-5 group-hover:scale-110 transition-transform`}>
                                    <IconComponent className="w-8 h-8 text-white" />
                                </div>
                                
                                {/* Subject Name */}
                                <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-primary transition-colors">
                                    {subject.name}
                                </h3>
                                
                                {/* Topic Count */}
                                <p className="text-gray-500 text-sm mb-4">
                                    {topicCount} {topicCount === 1 ? 'topic' : 'topics'} available
                                </p>
                                
                                {/* Action */}
                                <div className="flex items-center gap-2 text-primary font-bold text-sm">
                                    <span>Explore Topics</span>
                                    <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                                </div>
                            </motion.button>
                        );
                    })}
                </div>

                {/* Empty State */}
                {subjects.length === 0 && !error && (
                    <div className="text-center py-20">
                        <BookOpen className="w-16 h-16 text-gray-200 mx-auto mb-4" />
                        <h3 className="text-xl font-bold text-gray-400 mb-2">No Subjects Found</h3>
                        <p className="text-gray-400">Check if the database is properly seeded with quiz topics.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default QuizTopicsPage;
