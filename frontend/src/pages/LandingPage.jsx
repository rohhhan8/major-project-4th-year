import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Navbar from '../components/navbar/Navbar';
import { Upload, Link as LinkIcon, Sparkles, Search, ArrowRight, ArrowUpRight } from 'lucide-react';
import { motion } from 'framer-motion';
import LinkPasteModal from '../components/modals/LinkPasteModal';
import FileUploadModal from '../components/modals/FileUploadModal';

const LandingPage = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [showLinkModal, setShowLinkModal] = useState(false);
    const [showUploadModal, setShowUploadModal] = useState(false);
    const navigate = useNavigate();

    const handleSearch = (e) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            navigate(`/results?search_query=${encodeURIComponent(searchQuery)}`);
        }
    };

    // Extract YouTube video ID from various URL formats
    const extractYouTubeVideoId = (url) => {
        const patterns = [
            /(?:youtube\.com\/watch\?v=)([\w-]{11})/,
            /(?:youtube\.com\/embed\/)([\w-]{11})/,
            /(?:youtu\.be\/)([\w-]{11})/,
            /(?:youtube\.com\/shorts\/)([\w-]{11})/
        ];
        for (const pattern of patterns) {
            const match = url.match(pattern);
            if (match) return match[1];
        }
        return null;
    };

    const [isProcessing, setIsProcessing] = useState(false);

    const handleLinkSubmit = async (url) => {
        const videoId = extractYouTubeVideoId(url);
        if (!videoId) {
            // Fallback: treat as search query
            navigate(`/results?search_query=${encodeURIComponent(url)}`);
            return;
        }
        
        // Show processing state
        setIsProcessing(true);
        
        try {
            // Call transcript pipeline to process the video
            const response = await fetch('http://localhost:8000/transcript/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ video_id: videoId })
            });
            
            const data = await response.json();
            console.log('Transcript pipeline response:', data);
            
            // Navigate to video player with the actual title
            const title = data.title || 'YouTube Video';
            navigate(`/video?v=${videoId}&title=${encodeURIComponent(title)}`);
            
        } catch (error) {
            console.error('Error processing video:', error);
            // Still navigate even if processing fails
            navigate(`/video?v=${videoId}&title=YouTube%20Video`);
        } finally {
            setIsProcessing(false);
        }
    };

    const handleFileUpload = (file) => {
        console.log('File uploaded:', file);
        // TODO: Implement actual file upload to backend
        navigate('/notes');
    };

    const FeatureCard = ({ icon: Icon, title, subtitle, onClick, link, delay, compact }) => {
        const Content = (
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: delay }}
                className="relative block h-full min-h-[160px] bg-white rounded-3xl overflow-hidden group cursor-pointer border border-gray-100 shadow-sm transition-all duration-300 hover:border-transparent"
                onClick={onClick}
            >
                {/* Expanding Circle Background - Forced Green */}
                <div className="absolute top-[-30px] right-[-30px] w-20 h-20 rounded-full bg-emerald-600 transition-transform duration-500 ease-in-out origin-center transform scale-1 group-hover:scale-[35] z-0"></div>

                {/* Go Corner & Icon */}
                <div className="absolute top-0 right-0 w-14 h-14 flex items-center justify-center bg-emerald-600/10 rounded-bl-[32px] z-10 transition-colors duration-300 group-hover:bg-transparent">
                    <ArrowUpRight className="text-emerald-600 mb-1 mr-[-4px] group-hover:text-white transition-colors duration-300" size={20} />
                </div>

                {/* Main Content */}
                <div className="relative z-10 p-6 flex flex-col h-full items-start justify-center">
                    <div className="mb-4 p-3 rounded-full bg-emerald-600/10 text-emerald-600 group-hover:bg-white/20 group-hover:text-white transition-colors duration-300">
                        <Icon size={24} strokeWidth={2} />
                    </div>

                    <h3 className="text-xl font-bold text-gray-900 mb-2 transition-colors duration-300 group-hover:text-white leading-tight">
                        {title}
                    </h3>
                    <p className="text-sm font-medium text-gray-500 transition-colors duration-300 group-hover:text-white/90 leading-relaxed">
                        {subtitle}
                    </p>
                </div>
            </motion.div>
        );

        return link ? <Link to={link} className="block h-full">{Content}</Link> : Content;
    };

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans">
            <Navbar />

            <main className="flex-1 flex flex-col pt-32 pb-20 px-6 max-w-7xl mx-auto w-full relative z-10">

                {/* Hero Section - Split Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-24 items-center mb-24">

                    {/* Left: Content */}
                    <div className="max-w-2xl"> {/* Increased width from max-w-xl */}
                        <motion.h1
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8, ease: "easeOut" }}
                            className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-foreground tracking-tight leading-[1.1] mb-8 text-balance"
                        >
                            Learn something <span className="text-primary">new</span> <span className="relative inline-block">
                                <span className="relative z-10">every day.</span>
                                <svg className="absolute -bottom-2 left-0 w-full h-3 text-yellow-400 -z-0" viewBox="0 0 100 10" preserveAspectRatio="none">
                                    <path d="M0 5 Q 50 10 100 5" stroke="currentColor" strokeWidth="3" fill="none" />
                                </svg>
                            </span>
                        </motion.h1>

                        <motion.p
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
                            className="text-xl text-gray-500 font-medium mb-10 leading-relaxed max-w-lg"
                        >
                            Get key ideas from videos, podcasts, and articles. <br className="hidden md:block" />
                            Master any topic in minutes with AI-powered notes.
                        </motion.p>

                        {/* Search Bar - Minimalist */}
                        <motion.form
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: 0.4 }}
                            onSubmit={handleSearch}
                            className="relative flex items-center max-w-xl group"
                        >
                            <div className="absolute left-4 text-gray-400 group-focus-within:text-primary transition-colors">
                                <Search size={22} />
                            </div>
                            <input
                                id="search-input"
                                type="text"
                                placeholder="What do you want to learn?"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full pl-12 pr-4 py-4 rounded-full bg-gray-50 border border-gray-200 focus:bg-white focus:border-primary focus:ring-4 focus:ring-primary/10 transition-all outline-none text-lg font-bold text-gray-900 placeholder-gray-400"
                            />
                        </motion.form>

                        {/* Core Action Cards - Moved Below Search */}
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: 0.5 }}
                            className="mt-8 grid grid-cols-3 gap-4 max-w-xl"
                        >
                            <FeatureCard
                                icon={Upload}
                                title="Upload"
                                subtitle="File/Audio"
                                onClick={() => setShowUploadModal(true)}
                                delay={0.6}
                                compact={true}
                            />
                            <FeatureCard
                                icon={LinkIcon}
                                title="Paste"
                                subtitle="Link/Text"
                                onClick={() => setShowLinkModal(true)}
                                delay={0.7}
                                compact={true}
                            />
                            <FeatureCard
                                icon={Sparkles}
                                title="Quiz"
                                subtitle="Test Info"
                                link="/quiz/topics"
                                delay={0.8}
                                compact={true}
                            />
                        </motion.div>
                    </div>

                    {/* Right: Abstract Micro-Illustration (Framer Motion) */}
                    <div className="relative h-[600px] hidden lg:flex items-center justify-center">
                        {/* Geometric "Book" Construction */}
                        <motion.div
                            initial={{ transform: "perspective(1000px) rotateY(-10deg) rotateX(5deg)" }}
                            animate={{
                                transform: [
                                    "perspective(1000px) rotateY(-10deg) rotateX(5deg) translateY(0px)",
                                    "perspective(1000px) rotateY(-5deg) rotateX(2deg) translateY(-20px)",
                                    "perspective(1000px) rotateY(-10deg) rotateX(5deg) translateY(0px)"
                                ]
                            }}
                            transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
                            className="relative w-80 h-96 z-20"
                        >
                            {/* Back Cover */}
                            <div className="absolute inset-0 bg-gray-800 rounded-r-2xl rounded-l-md transform translate-z-[-20px] shadow-2xl"></div>

                            {/* Pages Stack */}
                            {[1, 2, 3, 4, 5].map((i) => (
                                <div
                                    key={i}
                                    className="absolute inset-y-2 left-0 w-[98%] bg-white border-r border-gray-200 rounded-r-xl"
                                    style={{ transform: `translateZ(${i * 2}px) translateX(${i}px)` }}
                                ></div>
                            ))}

                            {/* Front Cover - Duller Color */}
                            <div className="absolute inset-0 bg-emerald-800 rounded-r-2xl rounded-l-md shadow-inner flex flex-col items-center justify-center p-8 transform translate-z-[15px]"> {/* Duller: emerald-800 */}
                                <div className="w-16 h-16 bg-white/10 rounded-full mb-6 backdrop-blur-sm flex items-center justify-center">
                                    <Sparkles className="text-white/80" size={32} />
                                </div>
                                <div className="h-4 w-3/4 bg-white/10 rounded-full mb-3"></div>
                                <div className="h-4 w-1/2 bg-white/10 rounded-full"></div>

                                {/* Decoration */}
                                <div className="absolute bottom-0 right-0 w-32 h-32 bg-white/5 rounded-tl-[100px]"></div>
                            </div>
                        </motion.div>

                        {/* Floating Elements around the book */}
                        <motion.div
                            animate={{ y: [0, -15, 0], opacity: [0.8, 1, 0.8] }}
                            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", delay: 1 }}
                            className="absolute top-20 right-10 bg-white p-4 rounded-xl shadow-lg border border-gray-100 z-30"
                        >
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-600 font-bold">A+</div>
                                <div className="text-xs font-bold text-gray-600">Smart Notes</div>
                            </div>
                        </motion.div>

                        <motion.div
                            animate={{ y: [0, 20, 0], x: [0, -10, 0] }}
                            transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
                            className="absolute bottom-32 left-0 bg-white p-4 rounded-xl shadow-lg border border-gray-100 z-30"
                        >
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                                    <Upload size={14} />
                                </div>
                                <div className="text-xs font-bold text-gray-600">Processing...</div>
                            </div>
                        </motion.div>

                        {/* Background Glow */}
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-radial from-primary/10 to-transparent blur-3xl -z-10"></div>
                    </div>
                </div>

            </main >

            {/* Modals */}
            <LinkPasteModal
                isOpen={showLinkModal}
                onClose={() => setShowLinkModal(false)}
                onSubmit={handleLinkSubmit}
            />
            <FileUploadModal
                isOpen={showUploadModal}
                onClose={() => setShowUploadModal(false)}
                onUpload={handleFileUpload}
            />
        </div >
    );
};

export default LandingPage;
