import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Trophy, Flame, BarChart2, BookOpen, Clock, ArrowRight, Play, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    ArcElement,
    Title,
    Tooltip,
    Legend,
    Filler
} from 'chart.js';
import { Line, Doughnut } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    ArcElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

const StatCard = ({ icon: Icon, label, value, subtext, color, delay }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay }}
        className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all hover:-translate-y-1"
    >
        <div className="flex items-start justify-between mb-4">
            <div className={`p-3 rounded-xl ${color} bg-opacity-10 text-opacity-100`}>
                <Icon size={24} className={color.replace('bg-', 'text-')} />
            </div>
            {subtext && <span className="text-xs font-bold text-green-500 bg-green-50 px-2 py-1 rounded-full">{subtext}</span>}
        </div>
        <h3 className="text-gray-500 font-bold text-sm mb-1">{label}</h3>
        <p className="text-3xl font-extrabold text-gray-900">{value}</p>
    </motion.div>
);

const SectionHeader = ({ title, link, linkText }) => (
    <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 tracking-tight">{title}</h2>
        {link && (
            <Link to={link} className="text-sm font-bold text-primary hover:text-primary-hover flex items-center gap-1 transition-colors">
                {linkText} <ArrowRight size={16} />
            </Link>
        )}
    </div>
);

const VideoProgressCard = ({ video, delay }) => (
    <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay }}
    >
        <Link 
            to={`/video?v=${video.video_id}&title=${encodeURIComponent(video.title)}`}
            className="flex gap-4 p-4 bg-white rounded-2xl border border-gray-100 hover:border-primary/30 hover:shadow-lg transition-all group"
        >
            <div className="relative w-32 h-20 rounded-lg overflow-hidden flex-shrink-0 bg-gray-100">
                {video.thumbnail ? (
                    <img src={video.thumbnail} alt={video.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                ) : (
                    <div className="w-full h-full bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center">
                        <Play size={24} className="text-primary" />
                    </div>
                )}
                <div className="absolute inset-0 flex items-center justify-center bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Play size={20} className="text-white fill-current" />
                </div>
            </div>
            <div className="flex-1 flex flex-col justify-center">
                <h4 className="font-bold text-gray-900 text-sm line-clamp-1 mb-1 group-hover:text-primary transition-colors">{video.title}</h4>
                <p className="text-xs text-gray-500 font-medium mb-3">{video.category || 'Learning'}</p>
                <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${video.progress || 0}%` }}></div>
                </div>
            </div>
        </Link>
    </motion.div>
);

// Quiz Performance Chart Component
const QuizPerformanceChart = ({ quizData }) => {
    // Generate last 7 days labels
    const labels = [];
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { weekday: 'short' }));
    }

    // Simulate quiz scores (in real app, fetch from API)
    const scores = quizData?.length > 0 
        ? quizData.slice(-7).map(q => q.percentage || 0)
        : [65, 72, 58, 80, 75, 85, quizData?.avg || 70];

    const data = {
        labels,
        datasets: [
            {
                label: 'Quiz Score %',
                data: scores,
                fill: true,
                backgroundColor: (context) => {
                    const ctx = context.chart.ctx;
                    const gradient = ctx.createLinearGradient(0, 0, 0, 200);
                    gradient.addColorStop(0, 'rgba(16, 185, 129, 0.3)');
                    gradient.addColorStop(1, 'rgba(16, 185, 129, 0)');
                    return gradient;
                },
                borderColor: 'rgb(16, 185, 129)',
                borderWidth: 3,
                tension: 0.4,
                pointBackgroundColor: 'white',
                pointBorderColor: 'rgb(16, 185, 129)',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
            }
        ]
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: 'white',
                titleColor: '#1f2937',
                bodyColor: '#1f2937',
                borderColor: '#e5e7eb',
                borderWidth: 1,
                padding: 12,
                boxPadding: 6,
                usePointStyle: true,
                callbacks: {
                    label: (context) => `Score: ${context.parsed.y}%`
                }
            }
        },
        scales: {
            x: {
                grid: { display: false },
                ticks: { color: '#9ca3af', font: { weight: '600' } }
            },
            y: {
                beginAtZero: true,
                max: 100,
                grid: { color: '#f3f4f6' },
                ticks: { 
                    color: '#9ca3af', 
                    font: { weight: '600' },
                    callback: (value) => value + '%'
                }
            }
        },
        interaction: {
            intersect: false,
            mode: 'index'
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm"
        >
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="font-bold text-gray-900 text-lg">Quiz Performance</h3>
                    <p className="text-sm text-gray-500">Last 7 days trend</p>
                </div>
                <div className="flex items-center gap-2 text-green-500 bg-green-50 px-3 py-1 rounded-full">
                    <TrendingUp size={16} />
                    <span className="text-sm font-bold">+12%</span>
                </div>
            </div>
            <div className="h-48">
                <Line data={data} options={options} />
            </div>
        </motion.div>
    );
};

// Topic Distribution Chart Component
const TopicDistributionChart = ({ videosWatched }) => {
    const data = {
        labels: ['DSA', 'Frontend', 'Backend', 'System Design', 'Other'],
        datasets: [{
            data: [35, 25, 20, 12, 8],
            backgroundColor: [
                'rgb(59, 130, 246)',   // Blue - DSA
                'rgb(168, 85, 247)',   // Purple - Frontend
                'rgb(16, 185, 129)',   // Green - Backend
                'rgb(249, 115, 22)',   // Orange - System Design
                'rgb(156, 163, 175)',  // Gray - Other
            ],
            borderWidth: 0,
            hoverOffset: 8
        }]
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    usePointStyle: true,
                    pointStyle: 'circle',
                    padding: 15,
                    font: { size: 12, weight: '600' },
                    color: '#4b5563'
                }
            },
            tooltip: {
                backgroundColor: 'white',
                titleColor: '#1f2937',
                bodyColor: '#1f2937',
                borderColor: '#e5e7eb',
                borderWidth: 1,
                padding: 12,
                callbacks: {
                    label: (context) => `${context.label}: ${context.parsed}%`
                }
            }
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm"
        >
            <h3 className="font-bold text-gray-900 text-lg mb-2">Learning Focus</h3>
            <p className="text-sm text-gray-500 mb-4">Topics you've studied</p>
            <div className="h-48">
                <Doughnut data={data} options={options} />
            </div>
        </motion.div>
    );
};

const DashboardPage = () => {
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const response = await axios.get('http://localhost:8000/progress/dashboard', { withCredentials: true });
                setDashboardData(response.data);
            } catch (err) {
                console.error("Error fetching dashboard data:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchDashboardData();
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-white flex items-center justify-center">
                <div className="text-center">
                    <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-gray-500 font-medium">Loading your dashboard...</p>
                </div>
            </div>
        );
    }

    const stats = [
        { icon: Trophy, label: 'Avg. Quiz Score', value: `${dashboardData?.avg_quiz_score?.avg || 0}%`, color: 'bg-yellow-500 text-yellow-600', subtext: '+12%' },
        { icon: Flame, label: 'Weekly Streak', value: `${dashboardData?.weekly_streak?.current || 0} Days`, color: 'bg-orange-500 text-orange-600', subtext: 'On Fire!' },
        { icon: BarChart2, label: 'Course Progress', value: `${dashboardData?.learning_progress || 0}%`, color: 'bg-blue-500 text-blue-600', subtext: 'Keep it up' },
    ];

    return (
        <div className="min-h-screen bg-white font-sans pb-20">
            <div className="max-w-7xl mx-auto px-6 pt-8">

                {/* Header */}
                <header className="mb-12">
                    <motion.h1
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-3xl font-extrabold text-gray-900 mb-2"
                    >
                        Good afternoon, {dashboardData?.user_name || 'Learner'} 👋
                    </motion.h1>
                    <p className="text-gray-500 font-medium">Ready to continue learning something new?</p>
                </header>

                {/* Main Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                    {/* Left Column - Main Content */}
                    <div className="lg:col-span-2 space-y-8">

                        {/* Stats Row */}
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                            {stats.map((stat, i) => (
                                <StatCard key={stat.label} {...stat} delay={i * 0.1} />
                            ))}
                        </div>

                        {/* Quiz Performance Chart */}
                        <QuizPerformanceChart quizData={dashboardData?.quizzes || []} />

                        {/* Continue Learning - Limit to 3 */}
                        <div>
                            <SectionHeader title="Jump back in" link="/videos" linkText="View all history" />
                            <div className="grid grid-cols-1 gap-4">
                                {dashboardData?.ongoing_videos?.length > 0 ? (
                                    dashboardData.ongoing_videos.slice(0, 3).map((vid, i) => (
                                        <VideoProgressCard key={vid.video_id || vid.title} video={vid} delay={0.3 + (i * 0.1)} />
                                    ))
                                ) : (
                                    <motion.div 
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="bg-gradient-to-br from-gray-50 to-white p-8 rounded-2xl border border-gray-100 text-center"
                                    >
                                        <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                            <Play size={32} className="text-primary" />
                                        </div>
                                        <h3 className="font-bold text-gray-900 text-lg mb-2">Start Your Learning Journey</h3>
                                        <p className="text-gray-500 text-sm mb-6">Watch videos and take quizzes to track your progress</p>
                                        <div className="flex flex-col sm:flex-row gap-3 justify-center">
                                            <Link 
                                                to="/quiz/topics" 
                                                className="bg-primary hover:bg-primary/90 text-white font-bold py-3 px-6 rounded-xl text-sm transition-colors shadow-lg shadow-primary/20"
                                            >
                                                📝 Take a Quiz
                                            </Link>
                                            <Link 
                                                to="/" 
                                                className="bg-gray-900 hover:bg-gray-800 text-white font-bold py-3 px-6 rounded-xl text-sm transition-colors"
                                            >
                                                🎬 Start Watching
                                            </Link>
                                        </div>
                                    </motion.div>
                                )}
                            </div>
                        </div>

                    </div>

                    {/* Right Column - Sidebar Widgets */}
                    <div className="space-y-6">

                        {/* Topic Distribution Chart */}
                        <TopicDistributionChart videosWatched={dashboardData?.ongoing_videos?.length || 0} />

                        {/* Daily Goal Widget */}
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.5, delay: 0.6 }}
                            className="bg-gray-900 text-white p-6 rounded-3xl relative overflow-hidden"
                        >
                            <div className="relative z-10 w-full">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="font-bold text-lg">Daily Goal</h3>
                                    <Clock size={20} className="text-gray-400" />
                                </div>
                                <div className="text-4xl font-extrabold mb-2">45<span className="text-lg text-gray-400 font-normal">/60 min</span></div>
                                <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                                    <div className="bg-primary h-full w-[75%] rounded-full"></div>
                                </div>
                            </div>
                            {/* Decoration */}
                            <div className="absolute top-0 right-0 w-32 h-32 bg-primary blur-3xl opacity-20 transform translate-x-10 -translate-y-10"></div>
                        </motion.div>

                        {/* Recommended Topic */}
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.5, delay: 0.7 }}
                            className="bg-orange-50 p-6 rounded-3xl border border-orange-100"
                        >
                            <div className="mb-4 bg-white w-12 h-12 rounded-xl flex items-center justify-center shadow-sm text-orange-500">
                                <BookOpen size={24} />
                            </div>
                            <h3 className="font-bold text-gray-900 text-lg mb-2">Try a Quiz?</h3>
                            <p className="text-gray-600 text-sm mb-4 leading-relaxed">Boost your retention by taking a quick 5-minute quiz on your recent topics.</p>
                            <Link to="/quiz/topics" className="inline-block bg-orange-500 hover:bg-orange-600 text-white font-bold py-2.5 px-6 rounded-full text-sm transition-colors shadow-lg shadow-orange-500/20">
                                Start Quiz
                            </Link>
                        </motion.div>

                    </div>
                </div>
            </div>
        </div>
    );
};

export default DashboardPage;
