// src/pages/VideoPlayerPage.jsx
import React, { useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import YouTube from 'react-youtube';

const VideoPlayerPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const queryParams = new URLSearchParams(location.search);
    const videoId = queryParams.get('id');
    const title = queryParams.get('title');
    const playerRef = useRef(null);

    // --- Progress Tracking ---
    useEffect(() => {
        const interval = setInterval(() => {
            if (playerRef.current && typeof playerRef.current.getCurrentTime === 'function') {
                const player = playerRef.current;
                const currentTime = player.getCurrentTime();
                const duration = player.getDuration();

                if (duration > 0) {
                    const watchPercentage = (currentTime / duration) * 100;
                    axios.post('http://localhost:8000/progress/video', {
                        video_id: videoId,
                        watch_percentage: watchPercentage,
                        title: title,
                        category: "From Player", // This could be improved
                        instructor: "Unknown"
                    }, {
                        withCredentials: true
                    }).catch(err => console.error("Failed to send progress:", err));
                }
            }
        }, 10000); // Send progress update every 10 seconds

        return () => clearInterval(interval);
    }, [videoId, title]);

    const onReady = (event) => {
        playerRef.current = event.target;
    };

    const handleViewNotes = () => {
        navigate(`/notes?id=${videoId}&title=${encodeURIComponent(title)}`);
    };

    if (!videoId) {
        return <div className="p-8 text-center text-red-500">Video ID is missing.</div>;
    }
    
    const opts = {
        height: '390',
        width: '640',
        playerVars: {
          autoplay: 1,
        },
    };

    return (
        <div className="min-h-screen bg-gray-100 p-8">
            <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg">
                <div className="aspect-w-16 aspect-h-9 flex justify-center">
                    <YouTube videoId={videoId} opts={opts} onReady={onReady} />
                </div>
                <div className="p-6">
                    <h1 className="text-2xl font-bold mb-4">{title}</h1>
                    <button
                        onClick={handleViewNotes}
                        className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg"
                    >
                        View Notes
                    </button>
                </div>
            </div>
        </div>
    );
};

export default VideoPlayerPage;
