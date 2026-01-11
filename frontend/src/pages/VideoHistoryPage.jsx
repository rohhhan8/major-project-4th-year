// src/pages/VideoHistoryPage.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Play, Clock, ArrowLeft, Video, BookOpen } from 'lucide-react';

const VideoHistoryPage = () => {
    const [videos, setVideos] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await axios.get('http://localhost:8000/progress/dashboard', { 
                    withCredentials: true 
                });
                setVideos(response.data.ongoing_videos || []);
            } catch (err) {
                console.error("Error fetching video history:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchHistory();
    }, []);

    const SkeletonCard = () => (
        <div className="animate-pulse bg-white rounded-2xl border border-gray-100 p-4">
            <div className="flex gap-4">
                <div className="w-32 h-20 bg-gray-100 rounded-lg"></div>
                <div className="flex-1 space-y-3">
                    <div className="h-4 bg-gray-100 rounded w-3/4"></div>
                    <div className="h-3 bg-gray-100 rounded w-1/2"></div>
                    <div className="h-2 bg-gray-100 rounded w-full"></div>
                </div>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen bg-white font-sans pb-20">
            <div className="max-w-5xl mx-auto px-6 pt-8">
                
                {/* Header */}
                <div className="mb-8">
                    <Link to="/dashboard" className="inline-flex items-center gap-2 text-gray-500 hover:text-primary font-semibold mb-4 transition-colors">
                        <ArrowLeft size={18} />
                        Back to Dashboard
                    </Link>
                    <h1 className="text-3xl font-extrabold text-gray-900 flex items-center gap-3">
                        <Video className="text-primary" size={32} />
                        Video History
                    </h1>
                    <p className="text-gray-500 mt-2">All the videos you've watched</p>
                </div>

                {/* Video Grid */}
                {loading ? (
                    <div className="grid grid-cols-1 gap-4">
                        {[1, 2, 3, 4, 5].map(i => <SkeletonCard key={i} />)}
                    </div>
                ) : videos.length > 0 ? (
                    <div className="grid grid-cols-1 gap-4">
                        {videos.map((video, i) => (
                            <motion.div
                                key={video.video_id || i}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.4, delay: i * 0.05 }}
                            >
                                <Link 
                                    to={`/video?v=${video.video_id}&title=${encodeURIComponent(video.title)}`}
                                    className="flex gap-4 p-4 bg-white rounded-2xl border border-gray-100 hover:border-primary/30 hover:shadow-lg transition-all group"
                                >
                                    <div className="relative w-40 h-24 rounded-xl overflow-hidden flex-shrink-0 bg-gray-100">
                                        {video.thumbnail ? (
                                            <img 
                                                src={video.thumbnail} 
                                                alt={video.title} 
                                                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" 
                                            />
                                        ) : (
                                            <div className="w-full h-full bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center">
                                                <Play size={28} className="text-primary" />
                                            </div>
                                        )}
                                        <div className="absolute inset-0 flex items-center justify-center bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <Play size={24} className="text-white fill-current" />
                                        </div>
                                    </div>
                                    
                                    <div className="flex-1 flex flex-col justify-center">
                                        <h4 className="font-bold text-gray-900 text-lg mb-1 group-hover:text-primary transition-colors line-clamp-1">
                                            {video.title}
                                        </h4>
                                        <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                                            <span className="flex items-center gap-1">
                                                <BookOpen size={14} />
                                                {video.category || 'Learning'}
                                            </span>
                                            <span className="flex items-center gap-1">
                                                <Clock size={14} />
                                                {Math.round(video.progress || 0)}% watched
                                            </span>
                                        </div>
                                        <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                                            <div 
                                                className="h-full bg-primary rounded-full transition-all" 
                                                style={{ width: `${video.progress || 0}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                </Link>
                            </motion.div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-20 bg-gray-50 rounded-3xl border border-dashed border-gray-200">
                        <Video size={48} className="text-gray-300 mx-auto mb-4" />
                        <h3 className="text-xl font-bold text-gray-700 mb-2">No videos yet</h3>
                        <p className="text-gray-500 mb-6">Start watching videos to build your history</p>
                        <Link 
                            to="/home" 
                            className="inline-flex items-center gap-2 bg-primary text-white font-bold px-6 py-3 rounded-xl hover:bg-primary-hover transition-colors"
                        >
                            <Play size={18} />
                            Browse Videos
                        </Link>
                    </div>
                )}
            </div>
        </div>
    );
};

export default VideoHistoryPage;
