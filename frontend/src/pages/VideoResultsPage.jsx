import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../AuthContext';
import { Play } from 'lucide-react'; // Minimalist icon

const CategoryPill = ({ label, isActive, onClick }) => (
    <button
        onClick={onClick}
        className={`
            px-5 py-2 rounded-full font-bold text-sm whitespace-nowrap transition-all border
            ${isActive
                ? 'bg-black text-white border-black'
                : 'bg-white text-gray-600 border-gray-200 hover:border-gray-400 hover:text-gray-900'
            }
        `}
    >
        {label}
    </button>
);

const VideoCard = ({ video, isAuthenticated }) => {
    return (
        <Link
            to={isAuthenticated ? `/watch?id=${video.video_id}&title=${encodeURIComponent(video.title)}` : '/login'}
            className="group block"
        >
            <div className="bg-white rounded-xl overflow-hidden border border-transparent hover:border-gray-200 transition-all duration-300">
                {/* Thumbnail Container - Aspect Ratio 16:9 */}
                <div className="relative aspect-video bg-gray-100 overflow-hidden rounded-xl">
                    <img
                        src={video.thumbnail}
                        alt={video.title}
                        className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                    />
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors flex items-center justify-center">
                        <div className="w-12 h-12 bg-white/95 backdrop-blur-sm rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 translate-y-2 group-hover:translate-y-0 transition-all duration-300 shadow-sm">
                            <Play size={20} className="text-gray-900 fill-current ml-1" />
                        </div>
                    </div>
                </div>

                {/* Content */}
                <div className="pt-4 px-1">
                    <h3 className="font-bold text-gray-900 text-sm leading-snug line-clamp-2 mb-2 group-hover:text-primary transition-colors">
                        {video.title}
                    </h3>
                    <div className="flex items-center gap-2 text-xs text-gray-500 font-medium">
                        <span>{video.channelTitle || "YouTube"}</span>
                        <span>•</span>
                        <span>{video.publishTime ? new Date(video.publishTime).getFullYear() : "Recent"}</span>
                    </div>
                </div>
            </div>
        </Link>
    );
};

const VideoResultsPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { isAuthenticated } = useAuth();
    const [searchQuery, setSearchQuery] = useState('');
    const [videos, setVideos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeCategory, setActiveCategory] = useState('For You');

    const categories = ["For You", "Education", "Science", "History", "Computer Science", "Music", "Art", "Math"];

    useEffect(() => {
        const queryParams = new URLSearchParams(location.search);
        const query = queryParams.get('search_query');
        setSearchQuery(query);

        if (query) {
            fetchVideos(query);
        } else {
            // If no query, normally we'd load defaults. For now, just stop loading.
            setLoading(false);
        }
    }, [location]);

    const fetchVideos = async (query) => {
        try {
            setLoading(true);
            const response = await axios.get(`http://localhost:8000/video/search?query=${encodeURIComponent(query)}`);
            setVideos(response.data.videos);
            setError(null);
        } catch (err) {
            setError('Failed to fetch videos. Please try again later.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleCategoryClick = (category) => {
        setActiveCategory(category);
        navigate(`/results?search_query=${encodeURIComponent(category)}`);
    };

    return (
        <div className="max-w-[1600px] mx-auto pb-12 pt-8 px-6">
            {/* Header Section with Categories */}
            <div className="mb-10 space-y-6">
                <div className="flex items-center justify-between">
                    <h1 className="text-3xl font-extrabold tracking-tight text-gray-900">
                        {searchQuery ? `Results for "${searchQuery}"` : 'Explore'}
                    </h1>
                </div>

                {/* Category Pills Scroll Area */}
                <div className="flex items-center gap-3 overflow-x-auto pb-2 scrollbar-hide -mx-6 px-6 mask-fade-right">
                    {categories.map((cat) => (
                        <CategoryPill
                            key={cat}
                            label={cat}
                            isActive={activeCategory === cat}
                            onClick={() => handleCategoryClick(cat)}
                        />
                    ))}
                </div>
            </div>

            {/* Content Area */}
            {loading ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-x-6 gap-y-10 animate-pulse">
                    {[...Array(8)].map((_, i) => (
                        <div key={i}>
                            <div className="bg-gray-100 rounded-xl aspect-video mb-4"></div>
                            <div className="h-4 bg-gray-100 rounded w-3/4 mb-2"></div>
                            <div className="h-3 bg-gray-100 rounded w-1/2"></div>
                        </div>
                    ))}
                </div>
            ) : error ? (
                <div className="text-center py-20">
                    <p className="text-red-500 font-medium">{error}</p>
                </div>
            ) : (
                <>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-x-6 gap-y-10">
                        {videos.map(video => (
                            <VideoCard key={video.video_id} video={video} isAuthenticated={isAuthenticated} />
                        ))}
                    </div>

                    {!isAuthenticated && (
                        <div className="mt-20 p-10 bg-gray-50 rounded-3xl text-center border border-gray-100">
                            <h3 className="text-2xl font-bold text-gray-900 mb-3">Keep track of your learning.</h3>
                            <p className="text-gray-500 mb-8 max-w-md mx-auto text-lg">Sign in to save your history, take quizzes, and earn certificates.</p>
                            <Link
                                to="/login"
                                className="inline-flex items-center justify-center bg-primary hover:bg-primary-hover text-white font-bold py-3.5 px-8 rounded-full shadow-lg shadow-primary/25 transition-all hover:-translate-y-1"
                            >
                                Get Started for Free
                            </Link>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default VideoResultsPage;
