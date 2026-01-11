import React, { useState, useEffect } from 'react';
import { useLocation, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import {
    Plus, Search, Calendar, Clock, Tag, FileText,
    ChevronRight, Loader2, BookOpen, Lightbulb
} from 'lucide-react';

const NotesPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const queryParams = new URLSearchParams(location.search);
    const videoId = queryParams.get('id');
    const title = queryParams.get('title') || 'Untitled Note';

    const [notes, setNotes] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [notesHistory, setNotesHistory] = useState([]);
    const [historyLoading, setHistoryLoading] = useState(true);

    // Fetch notes history for sidebar
    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await axios.get('http://localhost:8000/notes/history', {
                    withCredentials: true
                });
                setNotesHistory(response.data.notes || []);
            } catch (err) {
                console.error("Error fetching notes history:", err);
            } finally {
                setHistoryLoading(false);
            }
        };
        fetchHistory();
    }, []);

    // Fetch or generate notes for current video
    useEffect(() => {
        if (videoId) {
            const fetchNotes = async () => {
                try {
                    setLoading(true);
                    const topic = queryParams.get('topic') || 'General Coding';
                    
                    const response = await axios.post('http://localhost:8000/notes/generate', {
                        topic: topic,
                        video_title: title,
                        video_id: videoId
                    }, { withCredentials: true });
                    
                    if (response.data.markdown) {
                        setNotes(response.data.markdown);
                    }
                    setError(null);
                } catch (err) {
                    console.error("Notes error:", err);
                    setError('Failed to generate notes. Please try again.');
                } finally {
                    setLoading(false);
                }
            };
            fetchNotes();
        } else {
            setLoading(false);
            setNotes('');
        }
    }, [videoId, title]);

    const handleNoteClick = (note) => {
        navigate(`/notes?id=${note.video_id}&title=${encodeURIComponent(note.video_title)}`);
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }).toUpperCase();
    };

    // Sidebar loading skeleton
    const SidebarSkeleton = () => (
        <div className="space-y-4 animate-pulse">
            {[1, 2, 3, 4].map(i => (
                <div key={i} className="p-3 rounded-xl">
                    <div className="h-3 bg-gray-100 rounded w-16 mb-2"></div>
                    <div className="h-4 bg-gray-100 rounded w-full mb-2"></div>
                    <div className="h-3 bg-gray-100 rounded w-3/4"></div>
                </div>
            ))}
        </div>
    );

    // Main content loading skeleton (educational themed)
    const ContentSkeleton = () => (
        <div className="space-y-6 animate-pulse">
            <div className="flex items-center gap-3 mb-8">
                <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
                    <Loader2 className="text-primary animate-spin" size={24} />
                </div>
                <div>
                    <div className="h-5 bg-gray-100 rounded w-48 mb-2"></div>
                    <div className="h-4 bg-gray-100 rounded w-32"></div>
                </div>
            </div>
            <div className="bg-primary/5 rounded-2xl p-6 border border-primary/10">
                <div className="flex items-center gap-3 mb-4">
                    <Lightbulb className="text-primary" size={20} />
                    <span className="font-bold text-primary">Generating your study notes...</span>
                </div>
                <p className="text-gray-600 text-sm">
                    Our AI is analyzing the video transcript and creating comprehensive notes tailored for learning.
                </p>
            </div>
            <div className="space-y-4">
                <div className="h-4 bg-gray-100 rounded w-3/4"></div>
                <div className="h-4 bg-gray-100 rounded w-full"></div>
                <div className="h-4 bg-gray-100 rounded w-5/6"></div>
                <div className="h-32 bg-gray-50 rounded-xl w-full"></div>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans">

            <div className="flex-1 flex pt-24 max-w-7xl mx-auto w-full px-6 gap-8">

                {/* Sidebar - Dynamic Notes History */}
                <aside className="w-64 hidden lg:flex flex-col gap-6 sticky top-24 h-[calc(100vh-8rem)]">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-6">My Notes</h2>
                        <Link 
                            to="/home"
                            className="w-full flex items-center gap-2 bg-primary/10 hover:bg-primary/20 text-primary font-bold py-2.5 px-4 rounded-xl transition-colors"
                        >
                            <Plus size={18} />
                            Generate new note
                        </Link>
                    </div>

                    <div className="flex-1 overflow-y-auto space-y-2 pr-2">
                        {historyLoading ? (
                            <SidebarSkeleton />
                        ) : notesHistory.length > 0 ? (
                            notesHistory.map((note, i) => (
                                <div 
                                    key={note.video_id + i}
                                    onClick={() => handleNoteClick(note)}
                                    className={`group cursor-pointer p-3 rounded-xl transition-all border ${
                                        videoId === note.video_id 
                                            ? 'bg-primary/5 border-primary/20' 
                                            : 'border-transparent hover:bg-gray-50 hover:border-gray-100'
                                    }`}
                                >
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="text-xs font-bold text-gray-400">
                                            {formatDate(note.generated_at)}
                                        </span>
                                    </div>
                                    <h3 className={`font-bold text-sm mb-1 line-clamp-2 transition-colors ${
                                        videoId === note.video_id ? 'text-primary' : 'text-gray-800 group-hover:text-primary'
                                    }`}>
                                        {note.video_title}
                                    </h3>
                                    <p className="text-xs text-gray-400 line-clamp-1">
                                        {note.topic || 'Study Notes'}
                                    </p>
                                </div>
                            ))
                        ) : (
                            <div className="text-center py-8 text-gray-400">
                                <FileText size={32} className="mx-auto mb-3 opacity-50" />
                                <p className="text-sm font-medium">No notes yet</p>
                                <p className="text-xs mt-1">Watch a video and generate notes!</p>
                            </div>
                        )}
                    </div>
                </aside>

                {/* Main Content */}
                <main className="flex-1 bg-white min-h-[500px] mb-20 rounded-3xl border border-gray-100 shadow-sm overflow-hidden flex flex-col">

                    {!videoId ? (
                        // Empty state - no video selected
                        <div className="flex-1 flex items-center justify-center p-12">
                            <div className="text-center max-w-md">
                                <div className="w-20 h-20 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
                                    <BookOpen size={40} className="text-primary" />
                                </div>
                                <h2 className="text-2xl font-bold text-gray-900 mb-3">Welcome to Notes</h2>
                                <p className="text-gray-500 mb-8">
                                    Select a note from the sidebar or watch a video to generate AI-powered study notes.
                                </p>
                                <Link 
                                    to="/home"
                                    className="inline-flex items-center gap-2 bg-primary text-white font-bold px-6 py-3 rounded-xl hover:bg-primary-hover transition-colors"
                                >
                                    <Plus size={18} />
                                    Generate New Notes
                                </Link>
                            </div>
                        </div>
                    ) : (
                        <>
                            {/* Header Metadata */}
                            <div className="p-8 border-b border-gray-50">
                                <div className="flex items-center gap-2 text-sm text-gray-400 font-medium mb-6">
                                    <span>My Notes</span>
                                    <ChevronRight size={14} />
                                    <span className="text-gray-900 line-clamp-1">{title}</span>
                                </div>

                                <h1 className="text-3xl font-extrabold text-gray-900 mb-6 tracking-tight leading-tight line-clamp-2">
                                    {title}
                                </h1>

                                <div className="flex flex-wrap gap-y-4 gap-x-8 text-sm text-gray-500">
                                    <div className="flex items-center gap-2">
                                        <div className="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold text-xs">
                                            AI
                                        </div>
                                        <span className="font-bold text-gray-700">Thinkly AI</span>
                                    </div>

                                    <div className="flex items-center gap-2">
                                        <Calendar size={16} />
                                        <span>{new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })}</span>
                                    </div>

                                    <div className="flex items-center gap-2">
                                        <Tag size={16} />
                                        <div className="flex gap-2">
                                            {['Study Notes', 'AI Generated'].map(tag => (
                                                <span key={tag} className="bg-gray-100 text-gray-600 px-2.5 py-0.5 rounded-md font-bold text-xs">{tag}</span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Content Area */}
                            <div className="flex-1 p-8 lg:p-12">
                                {loading ? (
                                    <ContentSkeleton />
                                ) : error ? (
                                    <div className="text-red-500 bg-red-50 p-4 rounded-lg text-sm font-bold flex items-center gap-2">
                                        <span>⚠️</span> {error}
                                    </div>
                                ) : (
                                    <div className="notes-content">
                                        <style>{`
                                            .notes-content h1 { font-size: 2rem; font-weight: 700; color: #1f2937; margin-bottom: 1.5rem; padding-bottom: 0.75rem; border-bottom: 2px solid #e5e7eb; }
                                            .notes-content h2 { font-size: 1.5rem; font-weight: 600; color: #374151; margin-top: 2.5rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #f3f4f6; }
                                            .notes-content h3 { font-size: 1.25rem; font-weight: 600; color: #4b5563; margin-top: 1.75rem; margin-bottom: 0.75rem; }
                                            .notes-content p { color: #4b5563; line-height: 1.8; margin-bottom: 1rem; }
                                            .notes-content ul { margin-top: 0.75rem; margin-bottom: 1.25rem; padding-left: 1.5rem; }
                                            .notes-content li { color: #4b5563; line-height: 1.75; margin-bottom: 0.5rem; }
                                            .notes-content li::marker { color: #10b981; }
                                            .notes-content code { background: #f3f4f6; color: #dc2626; padding: 0.2rem 0.4rem; border-radius: 0.25rem; font-size: 0.9em; }
                                            .notes-content pre { background: #1f2937; color: #e5e7eb; padding: 1.25rem; border-radius: 0.75rem; overflow-x: auto; margin: 1.5rem 0; font-size: 0.9rem; line-height: 1.6; }
                                            .notes-content pre code { background: transparent; color: #e5e7eb; padding: 0; }
                                            .notes-content strong { color: #1f2937; font-weight: 600; }
                                            .notes-content blockquote { border-left: 4px solid #10b981; padding-left: 1rem; margin: 1.5rem 0; color: #6b7280; font-style: italic; }
                                        `}</style>
                                        <ReactMarkdown>{notes}</ReactMarkdown>
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                </main>

            </div>
        </div>
    );
};

export default NotesPage;
