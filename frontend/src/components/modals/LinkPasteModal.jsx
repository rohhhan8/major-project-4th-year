import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Link as LinkIcon, ArrowRight } from 'lucide-react';

const LinkPasteModal = ({ isOpen, onClose, onSubmit }) => {
    const [url, setUrl] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();

        // Basic YouTube URL validation
        const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$/;

        if (!url.trim()) {
            setError('Please enter a URL');
            return;
        }

        if (!youtubeRegex.test(url)) {
            setError('Please enter a valid YouTube URL');
            return;
        }

        setError('');
        onSubmit(url);
        setUrl('');
        onClose();
    };

    const handleClose = () => {
        setUrl('');
        setError('');
        onClose();
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={handleClose}
                        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                    >
                        {/* Modal */}
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: 20 }}
                            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                            onClick={(e) => e.stopPropagation()}
                            className="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden"
                        >
                            {/* Header */}
                            <div className="bg-gradient-to-r from-emerald-600 to-emerald-700 p-6 relative">
                                <button
                                    onClick={handleClose}
                                    className="absolute top-4 right-4 text-white/80 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10"
                                >
                                    <X size={20} />
                                </button>
                                <div className="flex items-center gap-3">
                                    <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
                                        <LinkIcon className="text-white" size={24} />
                                    </div>
                                    <div>
                                        <h2 className="text-2xl font-bold text-white">Paste Link</h2>
                                        <p className="text-emerald-50 text-sm">Enter a YouTube URL to get started</p>
                                    </div>
                                </div>
                            </div>

                            {/* Form */}
                            <form onSubmit={handleSubmit} className="p-6 space-y-4">
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-2">
                                        YouTube URL
                                    </label>
                                    <input
                                        type="text"
                                        value={url}
                                        onChange={(e) => {
                                            setUrl(e.target.value);
                                            setError('');
                                        }}
                                        placeholder="https://www.youtube.com/watch?v=..."
                                        className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-emerald-600 focus:ring-4 focus:ring-emerald-600/10 transition-all outline-none font-medium text-gray-900 placeholder-gray-400"
                                        autoFocus
                                    />
                                    {error && (
                                        <motion.p
                                            initial={{ opacity: 0, y: -10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            className="text-red-500 text-sm font-medium mt-2"
                                        >
                                            {error}
                                        </motion.p>
                                    )}
                                </div>

                                <div className="flex gap-3 pt-2">
                                    <button
                                        type="button"
                                        onClick={handleClose}
                                        className="flex-1 px-6 py-3 rounded-xl font-bold text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className="flex-1 px-6 py-3 rounded-xl font-bold text-white bg-emerald-600 hover:bg-emerald-700 transition-colors flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20"
                                    >
                                        Continue
                                        <ArrowRight size={18} />
                                    </button>
                                </div>
                            </form>
                        </motion.div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};

export default LinkPasteModal;
