// src/components/dashboard/OngoingVideos.jsx
import React from 'react';

const VideoCard = ({ video }) => (
    <div className="group relative overflow-hidden rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
        <div className="relative pb-[56.25%] bg-gray-900">
            <img 
                src={video.thumbnail} 
                alt={video.title} 
                className="absolute top-0 left-0 w-full h-full object-cover"
            />
            {/* Play Icon Overlay */}
            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all flex items-center justify-center">
                <svg 
                    className="w-12 h-12 text-white opacity-0 group-hover:opacity-100 transition-opacity"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path d="M8 5v14l11-7z"/>
                </svg>
            </div>
            {/* Duration Badge */}
            <div className="absolute bottom-2 right-2 bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded">
                {video.duration || "45m"}
            </div>
        </div>
        
        <div className="p-4">
            <h4 className="font-semibold text-gray-900 mb-1 truncate">{video.title}</h4>
            <p className="text-xs text-gray-600 mb-3">
                {video.category} by {video.instructor}
            </p>
            
            <div className="space-y-2">
                <div className="flex items-center justify-between text-xs text-gray-600">
                    <span>Progress</span>
                    <span>{video.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div 
                        className="bg-blue-600 h-1.5 rounded-full transition-all" 
                        style={{ width: `${video.progress}%` }}
                    ></div>
                </div>
            </div>
            
            <button className="mt-3 w-full bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 rounded-lg transition-colors">
                Resume
            </button>
        </div>
    </div>
);

const OngoingVideos = ({ videos }) => {
    if (!videos || videos.length === 0) {
        return (
            <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
                <h4 className="text-sm font-medium text-gray-900 mb-4">Ongoing Videos</h4>
                <p className="text-sm text-gray-600">No videos in progress. Start learning something new!</p>
            </div>
        );
    }

    return (
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <h4 className="text-sm font-medium text-gray-900 mb-4">Ongoing Videos</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {videos.map((video, index) => (
                    <VideoCard key={index} video={video} />
                ))}
            </div>
        </div>
    );
};

export default OngoingVideos;
