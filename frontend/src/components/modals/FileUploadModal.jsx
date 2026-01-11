import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Upload, File, CheckCircle } from 'lucide-react';

const FileUploadModal = ({ isOpen, onClose, onUpload }) => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        const file = e.target.files?.[0];
        if (file) {
            setSelectedFile(file);
        }
    };

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setSelectedFile(e.dataTransfer.files[0]);
        }
    };

    const handleSubmit = () => {
        if (selectedFile) {
            onUpload(selectedFile);
            setSelectedFile(null);
            onClose();
        }
    };

    const handleClose = () => {
        setSelectedFile(null);
        onClose();
    };

    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={handleClose}
                        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                    >
                        {/* Modal */}
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: 20 }}
                            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                            onClick={(e) => e.stopPropagation()}
                            className="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden"
                        >
                            {/* Header */}
                            <div className="bg-gradient-to-r from-emerald-600 to-emerald-700 p-6 relative">
                                <button
                                    onClick={handleClose}
                                    className="absolute top-4 right-4 text-white/80 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10"
                                >
                                    <X size={20} />
                                </button>
                                <div className="flex items-center gap-3">
                                    <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
                                        <Upload className="text-white" size={24} />
                                    </div>
                                    <div>
                                        <h2 className="text-2xl font-bold text-white">Upload File</h2>
                                        <p className="text-emerald-50 text-sm">Upload audio or video files</p>
                                    </div>
                                </div>
                            </div>

                            {/* Upload Area */}
                            <div className="p-6 space-y-4">
                                <div
                                    onDragEnter={handleDrag}
                                    onDragLeave={handleDrag}
                                    onDragOver={handleDrag}
                                    onDrop={handleDrop}
                                    onClick={() => fileInputRef.current?.click()}
                                    className={`
                                        border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all
                                        ${dragActive
                                            ? 'border-emerald-600 bg-emerald-50'
                                            : 'border-gray-300 hover:border-emerald-600 hover:bg-gray-50'
                                        }
                                    `}
                                >
                                    <input
                                        ref={fileInputRef}
                                        type="file"
                                        onChange={handleFileChange}
                                        accept="audio/*,video/*"
                                        className="hidden"
                                    />

                                    {!selectedFile ? (
                                        <>
                                            <Upload className="mx-auto mb-4 text-gray-400" size={48} />
                                            <p className="text-lg font-bold text-gray-700 mb-2">
                                                Drop your file here or click to browse
                                            </p>
                                            <p className="text-sm text-gray-500">
                                                Supports audio and video files
                                            </p>
                                        </>
                                    ) : (
                                        <motion.div
                                            initial={{ scale: 0.8, opacity: 0 }}
                                            animate={{ scale: 1, opacity: 1 }}
                                            className="space-y-3"
                                        >
                                            <CheckCircle className="mx-auto text-emerald-600" size={48} />
                                            <div className="flex items-center justify-center gap-3 bg-gray-50 p-4 rounded-xl">
                                                <File className="text-emerald-600" size={24} />
                                                <div className="text-left">
                                                    <p className="font-bold text-gray-900 text-sm">{selectedFile.name}</p>
                                                    <p className="text-xs text-gray-500">{formatFileSize(selectedFile.size)}</p>
                                                </div>
                                            </div>
                                        </motion.div>
                                    )}
                                </div>

                                <div className="flex gap-3 pt-2">
                                    <button
                                        type="button"
                                        onClick={handleClose}
                                        className="flex-1 px-6 py-3 rounded-xl font-bold text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="button"
                                        onClick={handleSubmit}
                                        disabled={!selectedFile}
                                        className="flex-1 px-6 py-3 rounded-xl font-bold text-white bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors shadow-lg shadow-emerald-600/20"
                                    >
                                        Upload
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};

export default FileUploadModal;
