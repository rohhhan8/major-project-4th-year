// src/pages/DashboardPage.jsx
import React, { useState, useEffect, useLayoutEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import AvgQuizScore from '../components/dashboard/AvgQuizScore';
import WeeklyStreak from '../components/dashboard/WeeklyStreak';
import LearningProgress from '../components/dashboard/LearningProgress';
import OngoingVideos from '../components/dashboard/OngoingVideos';
import Calendar from '../components/dashboard/Calendar';
import UpcomingTasks from '../components/dashboard/UpcomingTasks';
import RecentActivity from '../components/dashboard/RecentActivity';

const StatCard = ({ title, value, subtitle, highestScore, lowestScore }) => (
    <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
        <div className="flex justify-between items-start mb-4">
            <div>
                <p className="text-gray-600 text-sm font-medium">{title}</p>
                <p className="text-3xl font-bold mt-1">{value}</p>
                <p className="text-gray-500 text-xs mt-1">{subtitle}</p>
            </div>
            <span className="text-red-500 text-sm font-medium">-10%</span>
        </div>
        {highestScore && lowestScore && (
            <div className="space-y-3 mt-4 border-t pt-4">
                <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Highest Score</span>
                    <span className="font-medium">{highestScore}%</span>
                </div>
                <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Lowest Score</span>
                    <span className="font-medium">{lowestScore}%</span>
                </div>
            </div>
        )}
    </div>
);

const DashboardPage = () => {
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useLayoutEffect(() => {
        const savedVideos = sessionStorage.getItem('video_results');
        if (savedVideos) {
            sessionStorage.removeItem('video_results'); // Clean up
            const videos = JSON.parse(savedVideos);
            // Redirect to home with videos before rendering dashboard
            navigate('/home', { state: { videos }, replace: true });
        }
    }, [navigate]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('http://localhost:8000/progress/dashboard', {
                    withCredentials: true
                });
                setDashboardData(response.data);
            } catch (err) {
                setError('Failed to load dashboard data.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) return <div className="text-center p-8 pt-24">Loading Dashboard...</div>;
    if (error) return <div className="text-red-500 text-center p-8 pt-24">{error}</div>;

    const learningProgressData = [
        { subject: "React Fundamentals", percentage: 75, color: "blue" },
        { subject: "JavaScript ES6+", percentage: 90, color: "green" },
        { subject: "CSS Grid & Flexbox", percentage: 60, color: "purple" },
        { subject: "TypeScript Basics", percentage: 45, color: "orange" },
    ];

    const upcomingTasksData = [
        { id: 1, task: "Complete React Quiz", time: "Today, 3:00 PM" },
        { id: 2, task: "Review TypeScript Notes", time: "Tomorrow, 10:00 AM" },
        { id: 3, task: "Watch CSS Grid Tutorial", time: "Nov 15, 2:00 PM" },
    ];

    const recentActivityData = [
        { id: 1, action: "Completed JavaScript Quiz", score: "85%", time: "2 hours ago" },
        { id: 2, action: "Watched React Hooks Tutorial", time: "5 hours ago" },
        { id: 3, action: "Generated notes for TypeScript video", time: "1 day ago" },
    ];

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="px-6 pb-12 max-w-7xl mx-auto">
                <div className="py-8">
                    <h1 className="text-3xl font-semibold mb-2">Welcome back, {dashboardData.user_name}!</h1>
                    <p className="text-gray-600">Here's your learning progress overview</p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left Column */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Stats Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <StatCard
                                title="Avg Quiz Score"
                                value={`${dashboardData.avg_quiz_score.avg}%`}
                                subtitle={`Highest Score: ${dashboardData.avg_quiz_score.highest}%`}
                                highestScore={dashboardData.avg_quiz_score.highest}
                                lowestScore={dashboardData.avg_quiz_score.lowest}
                            />
                            <WeeklyStreak data={dashboardData.weekly_streak} />
                        </div>

                        {/* Learning Progress */}
                        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
                            <h3 className="text-lg font-semibold mb-4">Learning Progress</h3>
                            <div className="space-y-4">
                                {learningProgressData.map((item) => (
                                    <div key={item.subject}>
                                        <div className="flex justify-between mb-2">
                                            <span className="text-sm font-medium text-gray-700">{item.subject}</span>
                                            <span className="text-sm font-medium text-gray-900">{item.percentage}%</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                            <div
                                                className={`h-2 rounded-full transition-all ${
                                                    item.color === 'blue' ? 'bg-blue-500' :
                                                    item.color === 'green' ? 'bg-green-500' :
                                                    item.color === 'purple' ? 'bg-purple-500' : 'bg-orange-500'
                                                }`}
                                                style={{ width: `${item.percentage}%` }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Ongoing Videos */}
                        <OngoingVideos videos={dashboardData.ongoing_videos} />
                    </div>

                    {/* Right Column */}
                    <div className="space-y-6">
                        <Calendar />
                        
                        {/* Upcoming Tasks */}
                        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
                            <h3 className="text-lg font-semibold mb-4">Upcoming Tasks</h3>
                            <div className="space-y-3">
                                {upcomingTasksData.map((task) => (
                                    <div key={task.id} className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                                        <p className="font-medium text-sm">{task.task}</p>
                                        <p className="text-xs text-gray-500 mt-1">{task.time}</p>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Recent Activity */}
                        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
                            <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
                            <div className="space-y-3">
                                {recentActivityData.map((activity, idx) => (
                                    <div key={activity.id} className={`pb-3 ${idx !== recentActivityData.length - 1 ? 'border-b' : ''}`}>
                                        <p className="font-medium text-sm">{activity.action}</p>
                                        {activity.score && <p className="text-sm text-green-600 font-medium mt-1">{activity.score}</p>}
                                        <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DashboardPage;
