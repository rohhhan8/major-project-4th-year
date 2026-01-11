// src/pages/QuizSubtopicsPage.jsx
/**
 * Quiz Subtopics Page - Shows all topics within a subject
 * 
 * User navigates here after clicking a subject on QuizTopicsPage.
 * Shows all subtopics as cards that can start a quiz.
 */

import React from 'react';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
    BookOpen, ArrowRight, ArrowLeft,
    Code, Coffee, Globe, Atom, Server, Palette, Database, Network, Cpu, Terminal
} from 'lucide-react';

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

const QuizSubtopicsPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { subjectId } = useParams();
    
    // Get subject data from navigation state
    const subject = location.state?.subject;
    
    // If no subject data, redirect back
    if (!subject) {
        return (
            <div className="min-h-screen bg-white flex items-center justify-center">
                <div className="text-center">
                    <BookOpen className="w-16 h-16 text-gray-200 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-gray-400 mb-4">Subject Not Found</h3>
                    <button 
                        onClick={() => navigate('/quiz/topics')}
                        className="text-primary font-bold hover:underline"
                    >
                        ← Back to Subjects
                    </button>
                </div>
            </div>
        );
    }

    const config = getSubjectConfig(subject._id);
    const IconComponent = config.icon;
    const topics = subject.topics || [];

    const startQuiz = (topicId) => {
        console.log('[QuizSubtopicsPage] Starting quiz for topic:', topicId);
        navigate(`/quiz/start/${topicId}`);
    };

    return (
        <div className="min-h-screen bg-white py-8 px-4">
            <div className="max-w-6xl mx-auto">
                
                {/* Back Button & Header */}
                <motion.div 
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-10"
                >
                    {/* Back Button */}
                    <button 
                        onClick={() => navigate('/quiz/topics')}
                        className="flex items-center gap-2 text-gray-500 hover:text-gray-900 font-medium mb-6 transition-colors"
                    >
                        <ArrowLeft size={18} />
                        Back to Subjects
                    </button>

                    {/* Subject Header */}
                    <div className="flex items-center gap-4">
                        <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${config.color} flex items-center justify-center shadow-lg`}>
                            <IconComponent className="w-8 h-8 text-white" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-extrabold text-gray-900">
                                {subject.name}
                            </h1>
                            <p className="text-gray-500">
                                {topics.length} {topics.length === 1 ? 'topic' : 'topics'} available
                            </p>
                        </div>
                    </div>
                </motion.div>

                {/* Topics Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {topics.map((topic, index) => (
                        <motion.button
                            key={topic._id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.03 }}
                            whileHover={{ y: -4, scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => startQuiz(topic._id)}
                            className="bg-white rounded-2xl border border-gray-100 p-5 text-left hover:shadow-lg hover:border-primary/30 transition-all group"
                        >
                            {/* Topic Icon/Emoji */}
                            <div className={`w-12 h-12 rounded-xl ${config.bgLight} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                                <span className="text-2xl">{topic.icon || '📄'}</span>
                            </div>
                            
                            {/* Topic Name */}
                            <h3 className="font-bold text-gray-900 mb-2 group-hover:text-primary transition-colors line-clamp-2">
                                {topic.name}
                            </h3>
                            
                            {/* Question Count & Action */}
                            <div className="flex items-center justify-between mt-3">
                                {topic.question_count > 0 ? (
                                    <span className={`text-xs font-semibold ${config.textColor} ${config.bgLight} px-2 py-1 rounded-full`}>
                                        {topic.question_count} Q
                                    </span>
                                ) : (
                                    <span className="text-xs text-gray-300">—</span>
                                )}
                                <div className="flex items-center gap-1 text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                                    <span className="text-xs font-bold">Start Quiz</span>
                                    <ArrowRight size={14} />
                                </div>
                            </div>
                        </motion.button>
                    ))}
                </div>

                {/* Empty State */}
                {topics.length === 0 && (
                    <div className="text-center py-20">
                        <BookOpen className="w-16 h-16 text-gray-200 mx-auto mb-4" />
                        <h3 className="text-xl font-bold text-gray-400 mb-2">No Topics Found</h3>
                        <p className="text-gray-400 mb-4">This subject doesn't have any topics yet.</p>
                        <button 
                            onClick={() => navigate('/quiz/topics')}
                            className="text-primary font-bold hover:underline"
                        >
                            ← Back to Subjects
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default QuizSubtopicsPage;
