// src/pages/VideoResultsPage.jsx
import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../AuthContext';

const VideoCard = ({ video, isAuthenticated }) => {
    const cardContent = (
        <div className="bg-white rounded-lg shadow-md overflow-hidden transform hover:-translate-y-1 transition-transform duration-300 cursor-pointer">
            <img src={video.thumbnail} alt={video.title} className="w-full h-48 object-cover" />
            <div className="p-4">
                <h3 className="font-bold text-lg">{video.title}</h3>
            </div>
        </div>
    );

    return isAuthenticated ? (
        <Link to={`/watch?id=${video.video_id}&title=${encodeURIComponent(video.title)}`}>{cardContent}</Link>
    ) : (
        <div>{cardContent}</div> // Not a link if not authenticated
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

    useEffect(() => {
        const queryParams = new URLSearchParams(location.search);
        const query = queryParams.get('search_query');
        setSearchQuery(query);

        if (query) {
            const fetchVideos = async () => {
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
            fetchVideos();
        }
    }, [location]);

    const handleLogin = () => {
        // Save videos to sessionStorage to retrieve after authentication
        sessionStorage.setItem('video_results', JSON.stringify(videos));
        navigate('/login');
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-7xl mx-auto">
                <h1 className="text-3xl font-bold mb-2">Results for "{searchQuery}"</h1>
                
                {!isAuthenticated && (
                    <p className="text-gray-600 mb-6">
                        Here are the top videos we found. Please sign in to watch and track your progress.
                    </p>
                )}

                {loading && <p className="text-center">Loading videos...</p>}
                {error && <p className="text-red-500 text-center">{error}</p>}

                {!loading && !error && (
                    <>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                            {videos.map(video => (
                                <VideoCard key={video.video_id} video={video} isAuthenticated={isAuthenticated} />
                            ))}
                        </div>
                        {!isAuthenticated && (
                            <div className="text-center mt-12">
                                <button
                                    onClick={handleLogin}
                                    className="bg-blue-600 hover:bg-blue-800 text-white font-bold py-3 px-6 rounded-lg shadow-lg text-lg"
                                >
                                    Sign in to Watch
                                </button>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
};

export default VideoResultsPage;
