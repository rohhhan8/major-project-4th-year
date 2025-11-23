// src/pages/NotesPage.jsx
import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';

const NotesPage = () => {
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const videoId = queryParams.get('id');
    const title = queryParams.get('title');

    const [notes, setNotes] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (videoId && title) {
            const fetchNotes = async () => {
                try {
                    setLoading(true);
                    const response = await axios.get(`http://localhost:8000/video/notes?video_id=${videoId}&title=${encodeURIComponent(title)}`);
                    setNotes(response.data.notes);
                    setError(null);
                } catch (err) {
                    setError('Failed to load notes. They may not be available for this video.');
                    console.error(err);
                } finally {
                    setLoading(false);
                }
            };
            fetchNotes();
        }
    }, [videoId, title]);

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-lg">
                <h1 className="text-3xl font-bold mb-4">Notes for: {title}</h1>
                
                {loading && <p>Generating notes, please wait...</p>}
                {error && <p className="text-red-500">{error}</p>}
                
                {!loading && !error && (
                    <div className="prose max-w-none">
                        {/* Using a pre-wrap to respect formatting from the AI */}
                        <p style={{ whiteSpace: 'pre-wrap' }}>{notes}</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default NotesPage;
