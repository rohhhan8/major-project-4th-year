// src/components/NotesCanvas.jsx
import React, { useState, useRef, useEffect, useCallback } from 'react';
import axios from 'axios';
import { 
    Bold, Italic, Underline, Highlighter, Type, 
    AlignLeft, AlignCenter, AlignRight, List, ListOrdered,
    Save, Check, Loader2, FileText
} from 'lucide-react';

const NotesCanvas = ({ videoId, videoTitle }) => {
    const editorRef = useRef(null);
    const [saveStatus, setSaveStatus] = useState('idle'); // idle, saving, saved
    const [lastSaved, setLastSaved] = useState(null);
    const saveTimeoutRef = useRef(null);

    // Toolbar colors
    const colors = ['#000000', '#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899'];
    const highlightColors = ['#fef08a', '#bbf7d0', '#bfdbfe', '#fbcfe8', '#fcd34d'];

    // Load existing notes on mount
    useEffect(() => {
        if (!videoId) return;
        
        const loadNotes = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/user-notes/${videoId}`, {
                    withCredentials: true
                });
                if (response.data.content && editorRef.current) {
                    editorRef.current.innerHTML = response.data.content;
                    if (response.data.updated_at) {
                        setLastSaved(new Date(response.data.updated_at));
                    }
                }
            } catch (err) {
                console.error("Failed to load notes:", err);
            }
        };
        loadNotes();
    }, [videoId]);

    // Auto-save with debounce
    const saveNotes = useCallback(async () => {
        if (!editorRef.current || !videoId) return;
        
        setSaveStatus('saving');
        try {
            await axios.post('http://localhost:8000/user-notes/save', {
                video_id: videoId,
                video_title: videoTitle,
                content: editorRef.current.innerHTML
            }, {
                withCredentials: true
            });
            setSaveStatus('saved');
            setLastSaved(new Date());
            setTimeout(() => setSaveStatus('idle'), 2000);
        } catch (err) {
            console.error("Failed to save notes:", err);
            setSaveStatus('idle');
        }
    }, [videoId, videoTitle]);

    // Debounced auto-save on input
    const handleInput = () => {
        if (saveTimeoutRef.current) {
            clearTimeout(saveTimeoutRef.current);
        }
        saveTimeoutRef.current = setTimeout(saveNotes, 3000); // Auto-save after 3 seconds of inactivity
    };

    // Execute command helper
    const execCmd = (command, value = null) => {
        document.execCommand(command, false, value);
        editorRef.current?.focus();
    };

    // Toolbar button component
    const ToolbarBtn = ({ icon: Icon, onClick, title, active }) => (
        <button
            onClick={onClick}
            title={title}
            className={`p-2 rounded-lg transition-all hover:bg-gray-100 ${active ? 'bg-indigo-100 text-indigo-600' : 'text-gray-600'}`}
        >
            <Icon size={18} />
        </button>
    );

    return (
        <div className="flex flex-col h-full bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50">
                <h3 className="font-bold text-gray-800 flex items-center gap-2">
                    <FileText size={18} className="text-primary" />
                    Your Notes
                </h3>
                <div className="flex items-center gap-2 text-sm">
                    {saveStatus === 'saving' && (
                        <span className="flex items-center gap-1 text-gray-500">
                            <Loader2 size={14} className="animate-spin" />
                            Saving...
                        </span>
                    )}
                    {saveStatus === 'saved' && (
                        <span className="flex items-center gap-1 text-green-600">
                            <Check size={14} />
                            Saved
                        </span>
                    )}
                    {saveStatus === 'idle' && lastSaved && (
                        <span className="text-gray-400 text-xs">
                            Last saved: {lastSaved.toLocaleTimeString()}
                        </span>
                    )}
                    <button
                        onClick={saveNotes}
                        className="flex items-center gap-1 px-3 py-1.5 bg-indigo-600 text-white text-xs font-bold rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                        <Save size={12} /> Save
                    </button>
                </div>
            </div>

            {/* Toolbar */}
            <div className="flex flex-wrap items-center gap-1 px-3 py-2 border-b border-gray-100 bg-white">
                <ToolbarBtn icon={Bold} onClick={() => execCmd('bold')} title="Bold (Ctrl+B)" />
                <ToolbarBtn icon={Italic} onClick={() => execCmd('italic')} title="Italic (Ctrl+I)" />
                <ToolbarBtn icon={Underline} onClick={() => execCmd('underline')} title="Underline (Ctrl+U)" />
                
                <div className="w-px h-6 bg-gray-200 mx-1" />
                
                {/* Text Colors */}
                <div className="flex items-center gap-0.5">
                    <Type size={14} className="text-gray-400 mr-1" />
                    {colors.map(color => (
                        <button
                            key={color}
                            onClick={() => execCmd('foreColor', color)}
                            className="w-5 h-5 rounded-full border border-gray-200 hover:scale-110 transition-transform"
                            style={{ backgroundColor: color }}
                            title={`Text color: ${color}`}
                        />
                    ))}
                </div>
                
                <div className="w-px h-6 bg-gray-200 mx-1" />
                
                {/* Highlight Colors */}
                <div className="flex items-center gap-0.5">
                    <Highlighter size={14} className="text-gray-400 mr-1" />
                    {highlightColors.map(color => (
                        <button
                            key={color}
                            onClick={() => execCmd('hiliteColor', color)}
                            className="w-5 h-5 rounded border border-gray-200 hover:scale-110 transition-transform"
                            style={{ backgroundColor: color }}
                            title={`Highlight: ${color}`}
                        />
                    ))}
                </div>
                
                <div className="w-px h-6 bg-gray-200 mx-1" />
                
                <ToolbarBtn icon={AlignLeft} onClick={() => execCmd('justifyLeft')} title="Align Left" />
                <ToolbarBtn icon={AlignCenter} onClick={() => execCmd('justifyCenter')} title="Align Center" />
                <ToolbarBtn icon={AlignRight} onClick={() => execCmd('justifyRight')} title="Align Right" />
                
                <div className="w-px h-6 bg-gray-200 mx-1" />
                
                <ToolbarBtn icon={List} onClick={() => execCmd('insertUnorderedList')} title="Bullet List" />
                <ToolbarBtn icon={ListOrdered} onClick={() => execCmd('insertOrderedList')} title="Numbered List" />
            </div>

            {/* Editor Area */}
            <div
                ref={editorRef}
                contentEditable
                onInput={handleInput}
                className="flex-1 p-4 overflow-y-auto focus:outline-none text-gray-700 leading-relaxed"
                style={{ minHeight: '300px' }}
                placeholder="Start typing your notes here..."
            />
            
            {/* Footer hint */}
            <div className="px-4 py-2 border-t border-gray-100 bg-gray-50 text-xs text-gray-400">
                Tip: Your notes auto-save after 3 seconds of inactivity
            </div>
        </div>
    );
};

export default NotesCanvas;
