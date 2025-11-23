// src/components/navbar/Navbar.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../AuthContext';

const Navbar = () => {
    const { isAuthenticated, user, logout } = useAuth();
    
    const handleLogout = () => {
        logout();
    };

    const navItems = [
        { path: '/dashboard', label: 'Dashboard' },
        { path: '/quiz/topics', label: 'Quizzes' },
        { path: '/videos', label: 'Videos' },
        { path: '/notes', label: 'Notes' },
    ];

    if (!isAuthenticated) {
        return null; // Don't render anything if not authenticated
    }

    return (
        <header className="fixed top-0 left-0 right-0 z-50 h-16 glass-nav">
            <div className="flex items-center justify-between h-full px-6 max-w-7xl mx-auto">
                {/* Logo */}
                <Link to="/home" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
                    <span className="text-2xl font-bold text-gray-900">Adaptive Learning</span>
                </Link>

                {/* Navigation Links */}
                {isAuthenticated && (
                    <nav className="flex items-center gap-6">
                        {navItems.map((item) => (
                            <Link
                                key={item.path}
                                to={item.path}
                                className="text-gray-600 hover:text-gray-900 font-medium text-sm transition-colors"
                            >
                                {item.label}
                            </Link>
                        ))}
                    </nav>
                )}

                {/* User Section */}
                <div className="flex items-center gap-4">
                    {isAuthenticated && user && (
                        <>
                            <span className="text-gray-800 font-medium text-sm">{user.name}</span>
                            <button
                                onClick={handleLogout}
                                className="text-gray-600 hover:text-gray-900 text-sm font-medium transition-colors px-3 py-2 rounded-lg hover:bg-gray-100"
                            >
                                Logout
                            </button>
                        </>
                    )}
                </div>
            </div>
        </header>
    );
};

export default Navbar;
