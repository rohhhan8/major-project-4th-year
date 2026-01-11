import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../AuthContext';
import { Home, LayoutDashboard, Video, FileText, Sparkles, LogOut, Flame, Brain } from 'lucide-react';
import { motion } from 'framer-motion';
import axios from 'axios';

const Navbar = () => {
    const { isAuthenticated, user, logout } = useAuth();
    const location = useLocation();
    const [streak, setStreak] = useState(0);

    // Fetch streak from dashboard data
    useEffect(() => {
        if (isAuthenticated) {
            const fetchStreak = async () => {
                try {
                    const response = await axios.get('http://localhost:8000/progress/dashboard', {
                        withCredentials: true
                    });
                    setStreak(response.data.weekly_streak?.current || 0);
                } catch (err) {
                    console.log('Could not fetch streak');
                }
            };
            fetchStreak();
        }
    }, [isAuthenticated]);

    // Don't show navbar on login page
    if (location.pathname === '/login') return null;

    const navItems = [
        { path: '/', label: 'Home', icon: Home },
        { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { path: '/quiz/topics', label: 'Quizzes', icon: Sparkles },
        { path: '/videos', label: 'Videos', icon: Video },
        { path: '/notes', label: 'Notes', icon: FileText },
    ];

    return (
        <div className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-100 shadow-sm">
            <header className="flex items-center justify-between px-6 py-3 max-w-7xl mx-auto">

                {/* Logo - Thinkly with Brain Icon */}
                <Link to="/" className="flex items-center gap-2.5 group">
                    <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/30 transition-transform group-hover:scale-105">
                        <Brain size={22} className="text-white" strokeWidth={2} />
                    </div>
                    <span className="text-xl font-black tracking-tight">
                        <span className="text-gray-900">Think</span>
                        <span className="text-emerald-600">ly</span>
                    </span>
                </Link>

                {/* Navigation Links (Desktop) */}
                <nav className="hidden md:flex items-center gap-1 bg-gray-50 rounded-xl p-1">
                    {isAuthenticated ? (
                        navItems.map((item) => {
                            const Icon = item.icon;
                            const isActive = location.pathname.startsWith(item.path);
                            return (
                                <motion.div
                                    key={item.path}
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                >
                                    <Link
                                        to={item.path}
                                        className={`
                                            flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all
                                            ${isActive
                                                ? 'bg-white text-emerald-600 shadow-sm'
                                                : 'text-gray-500 hover:text-gray-900 hover:bg-white/50'
                                            }
                                        `}
                                    >
                                        <Icon size={17} strokeWidth={isActive ? 2.5 : 2} />
                                        {item.label}
                                    </Link>
                                </motion.div>
                            );
                        })
                    ) : null}
                </nav>

                {/* User Section / Auth Buttons */}
                <div className="flex items-center gap-3">
                    {isAuthenticated && user ? (
                        <>
                            {/* Dynamic Streak Badge */}
                            {streak > 0 && (
                                <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 bg-orange-50 rounded-lg border border-orange-100">
                                    <Flame size={16} className="text-orange-500" />
                                    <span className="text-orange-600 text-sm font-bold">
                                        {streak} {streak === 1 ? 'day' : 'days'}
                                    </span>
                                </div>
                            )}

                            <div className="h-6 w-px bg-gray-200" />

                            {/* User Menu */}
                            <div className="flex items-center gap-2">
                                <div className="w-9 h-9 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center text-white font-bold text-sm shadow-md">
                                    {(user.name || user.full_name || 'U').charAt(0).toUpperCase()}
                                </div>
                                <button
                                    onClick={logout}
                                    className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all"
                                    title="Logout"
                                >
                                    <LogOut size={18} />
                                </button>
                            </div>
                        </>
                    ) : (
                        <>
                            <Link
                                to="/login"
                                className="hidden md:block text-gray-600 hover:text-gray-900 font-semibold text-sm px-4"
                            >
                                Log in
                            </Link>
                            <Link
                                to="/login"
                                className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-bold text-sm px-6 py-2.5 rounded-xl shadow-lg shadow-emerald-500/20 hover:shadow-xl transition-all hover:-translate-y-0.5"
                            >
                                Get Started
                            </Link>
                        </>
                    )}
                </div>
            </header>
        </div>
    );
};

export default Navbar;
