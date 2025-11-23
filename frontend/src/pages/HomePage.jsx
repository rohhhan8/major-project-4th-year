import React, { useState, useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';

const VideoCard = ({ video }) => {
    return (
        <Link to={`/watch?id=${video.video_id}&title=${encodeURIComponent(video.title)}`}>
            <div className="bg-white rounded-lg shadow-md overflow-hidden transform hover:-translate-y-1 transition-transform duration-300 cursor-pointer">
                <img src={video.thumbnail} alt={video.title} className="w-full h-48 object-cover" />
                <div className="p-4">
                    <h3 className="font-bold text-lg">{video.title}</h3>
                </div>
            </div>
        </Link>
    );
};

const HomePage = () => {
    const location = useLocation();
    const [videos, setVideos] = useState(location.state?.videos || []);

    useEffect(() => {
        // This effect ensures that if the user navigates to this page
        // with new state, the component updates.
        if (location.state?.videos) {
            setVideos(location.state.videos);
        } else {
            // Check session storage for videos from before login
            const storedVideos = sessionStorage.getItem('video_results');
            if (storedVideos) {
                setVideos(JSON.parse(storedVideos));
                sessionStorage.removeItem('video_results');
            }
        }
    }, [location.state]);

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold mb-4">Welcome Back!</h1>
            {videos.length > 0 ? (
                <>
                    <h2 className="text-2xl font-bold mb-4">Here are your videos</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {videos.map(video => (
                            <VideoCard key={video.video_id} video={video} />
                        ))}
                    </div>
                </>
            ) : (
                <div className="text-center py-16">
                    <p className="text-gray-600 text-lg">You don't have any videos here yet.</p>
                    <p className="text-gray-500 mt-2">Try searching for a topic from the landing page to get started!</p>
                </div>
            )}
        </div>
    );
};

export default HomePage;
