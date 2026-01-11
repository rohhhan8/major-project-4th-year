import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, Lock, User, ArrowRight, AlertCircle, Loader2, BookOpen } from 'lucide-react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';

const SignupPage = () => {
    const navigate = useNavigate();
    const { login } = useAuth();
    const [formData, setFormData] = useState({
        full_name: '',
        email: '',
        password: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [strength, setStrength] = useState(0);

    const checkStrength = (pass) => {
        let s = 0;
        if (pass.length > 6) s++;
        if (pass.length > 10) s++;
        if (/[A-Z]/.test(pass)) s++;
        if (/[0-9]/.test(pass)) s++;
        if (/[^A-Za-z0-9]/.test(pass)) s++;
        setStrength(s);
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        if (e.target.name === 'password') checkStrength(e.target.value);
    };

    const handleSignup = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const response = await axios.post('http://localhost:8000/auth/signup', formData, {
                withCredentials: true
            });
            // Update global auth state
            login(response.data);
            navigate('/dashboard'); // Changed from /home to /dashboard for better UX
        } catch (err) {
            setError(err.response?.data?.detail || "Registration failed. Try again.");
        } finally {
            setLoading(false);
        }
    };

    const getStrengthColor = () => {
        if (strength <= 1) return 'bg-red-400';
        if (strength <= 3) return 'bg-yellow-400';
        return 'bg-green-400';
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-md p-6"
            >
                {/* Header */}
                <div className="text-center mb-6">
                    <div className="flex justify-center mb-4">
                        <div className="p-3 bg-blue-500 rounded-xl shadow-md">
                            <BookOpen className="w-8 h-8 text-white" />
                        </div>
                    </div>
                    <h1 className="text-3xl font-bold text-gray-800">Create Account</h1>
                    <p className="text-gray-500 mt-1">Join the adaptive learning platform</p>
                </div>

                {/* Card */}
                <div className="bg-white rounded-lg shadow-md p-8">
                    {error && (
                        <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded-lg flex items-center gap-2">
                            <AlertCircle className="w-4 h-4" />
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSignup} className="space-y-4">
                        {/* Name */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                            <div className="relative">
                                <User className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                                <input 
                                    type="text" 
                                    name="full_name"
                                    required
                                    className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                                    placeholder="John Doe"
                                    value={formData.full_name}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>

                        {/* Email */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                                <input 
                                    type="email" 
                                    name="email"
                                    required
                                    className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                                    placeholder="john@example.com"
                                    value={formData.email}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>

                        {/* Password */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                                <input 
                                    type="password" 
                                    name="password"
                                    required
                                    className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                                    placeholder="••••••••"
                                    value={formData.password}
                                    onChange={handleChange}
                                />
                            </div>
                            
                            {/* Strength Meter */}
                            {formData.password && (
                                <div className="pt-2">
                                    <div className="flex gap-1 h-1.5">
                                        {[1, 2, 3, 4, 5].map((i) => (
                                            <div 
                                                key={i} 
                                                className={`flex-1 rounded-full transition-all duration-300 ${i <= strength ? getStrengthColor() : 'bg-gray-200'}`}
                                            />
                                        ))}
                                    </div>
                                    <p className="text-right text-xs text-gray-400 mt-1">
                                        {strength < 3 ? 'Weak' : strength < 5 ? 'Good' : 'Strong'}
                                    </p>
                                </div>
                            )}
                        </div>

                        <button 
                            type="submit" 
                            disabled={loading}
                            className="w-full py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-semibold shadow-md transition-all duration-200 flex items-center justify-center gap-2"
                        >
                            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Create Account"}
                            {!loading && <ArrowRight className="w-5 h-5" />}
                        </button>
                    </form>
                </div>

                {/* Footer */}
                <p className="text-center mt-6 text-gray-500">
                    Already have an account?{' '}
                    <Link to="/login" className="font-semibold text-blue-500 hover:text-blue-600">
                        Sign in
                    </Link>
                </p>
            </motion.div>
        </div>
    );
};

export default SignupPage;
