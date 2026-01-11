// src/pages/VideoPlayerPage.jsx
import React, { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import YouTube from 'react-youtube';
import { FileText, ArrowLeft, Clock, Award, ChevronDown, ChevronUp } from 'lucide-react';
import NotesCanvas from '../components/NotesCanvas';

const VideoPlayerPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const queryParams = new URLSearchParams(location.search);
    const paramId = queryParams.get('v') || queryParams.get('id');
    const videoId = paramId ? paramId.split('_')[0] : null;
    const title = queryParams.get('title') || 'Educational Video';
    const playerRef = useRef(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [loadingTranscript, setLoadingTranscript] = useState(true);
    const [transcriptExpanded, setTranscriptExpanded] = useState(true);

    // Load transcript from backend
    useEffect(() => {
        if (!videoId) return;
        
        const fetchTranscript = async () => {
            setLoadingTranscript(true);
            try {
                const response = await axios.get(`http://localhost:8000/video/transcript/${videoId}`);
                setTranscript(response.data.transcript || 'No transcript available for this video.');
            } catch (err) {
                console.error("Failed to load transcript:", err);
                setTranscript('Transcript not available.');
            } finally {
                setLoadingTranscript(false);
            }
        };
        fetchTranscript();
    }, [videoId]);

    // Progress tracking
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
                        category: "From Player",
                        instructor: "Unknown"
                    }, {
                        withCredentials: true
                    }).catch(err => console.error("Failed to send progress:", err));
                }
            }
        }, 10000);

        return () => clearInterval(interval);
    }, [videoId, title]);

    const onReady = (event) => {
        playerRef.current = event.target;
    };

    const onStateChange = (event) => {
        setIsPlaying(event.data === 1);
    };

    const handleViewNotes = () => {
        navigate(`/notes?id=${videoId}&title=${encodeURIComponent(title)}`);
    };

    if (!videoId) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center p-8 bg-white rounded-2xl shadow-xl">
                    <h2 className="text-xl font-bold text-gray-800">Video Not Found</h2>
                    <button 
                        onClick={() => navigate('/dashboard')}
                        className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-bold"
                    >
                        Go Home
                    </button>
                </div>
            </div>
        );
    }
    
    const opts = {
        height: '100%',
        width: '100%',
        playerVars: {
            autoplay: 0,
            modestbranding: 1,
            rel: 0,
        },
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col font-sans">

            {/* Main Content - Added more top padding for navbar */}
            <main className="flex-1 pt-24 pb-6 px-4 lg:px-6">
                <div className="max-w-[1600px] mx-auto">
                    
                    {/* Video Title Bar */}
                    <div className="flex items-center justify-between mb-4">
                        <div>
                            <h1 className="text-xl font-bold text-gray-900 line-clamp-1">{title}</h1>
                            <p className="text-sm text-gray-500 flex items-center gap-2 mt-0.5">
                                <Clock size={14} />
                                Learning Session
                            </p>
                        </div>
                        <button
                            onClick={handleViewNotes}
                            className="flex items-center gap-2 px-5 py-2.5 bg-primary text-primary-foreground text-sm font-bold rounded-xl hover:bg-primary-hover transition-colors shadow-lg shadow-primary/20"
                        >
                            <FileText size={16} />
                            Generate AI Notes
                        </button>
                    </div>

                    {/* Two Column Grid */}
                    <div className="h-[calc(100vh-11rem)] grid lg:grid-cols-2 gap-6">
                    
                    {/* Left Column: Video + Transcript */}
                    <div className="flex flex-col gap-4 overflow-hidden">
                        {/* Video Player */}
                        <div className="relative aspect-video bg-black rounded-2xl overflow-hidden shadow-xl ring-1 ring-black/5 flex-shrink-0">
                            <YouTube 
                                videoId={videoId} 
                                opts={opts} 
                                onReady={onReady} 
                                onStateChange={onStateChange}
                                className="absolute inset-0 w-full h-full"
                            />
                        </div>
                        
                        {/* Transcript Section */}
                        <div className="flex-1 bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden flex flex-col min-h-0">
                            <button 
                                onClick={() => setTranscriptExpanded(!transcriptExpanded)}
                                className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50 hover:bg-gray-100 transition-colors"
                            >
                                <h3 className="font-bold text-gray-800 flex items-center gap-2">
                                    <FileText size={18} className="text-primary" />
                                    Video Transcript
                                </h3>
                                {transcriptExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                            </button>
                            
                            {transcriptExpanded && (
                                <div className="flex-1 overflow-y-auto p-4">
                                    {loadingTranscript ? (
                                        <div className="space-y-3 animate-pulse">
                                            <div className="h-4 bg-gray-100 rounded w-full"></div>
                                            <div className="h-4 bg-gray-100 rounded w-5/6"></div>
                                            <div className="h-4 bg-gray-100 rounded w-4/5"></div>
                                        </div>
                                    ) : (
                                        <p className="text-gray-600 text-sm leading-relaxed whitespace-pre-wrap">
                                            {transcript}
                                        </p>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right Column: Notes Canvas */}
                    <div className="overflow-hidden">
                        <NotesCanvas videoId={videoId} videoTitle={title} />
                    </div>

                </div>
                </div>
            </main>
        </div>
    );
};

export default VideoPlayerPage;
