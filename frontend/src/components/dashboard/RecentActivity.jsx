// src/components/dashboard/RecentActivity.jsx
import React from 'react';

const ActivityItem = ({ activity, index }) => {
    const iconMap = {
        quiz: '✓',
        video: '▶',
        note: '📝',
        achievement: '⭐'
    };

    const colorMap = {
        quiz: 'bg-green-100 text-green-700',
        video: 'bg-blue-100 text-blue-700',
        note: 'bg-purple-100 text-purple-700',
        achievement: 'bg-yellow-100 text-yellow-700'
    };

    const type = activity.type || 'quiz';
    const icon = iconMap[type] || '•';
    const color = colorMap[type] || 'bg-gray-100 text-gray-700';

    return (
        <div className="flex gap-3 pb-3 border-b border-gray-100 last:border-b-0 last:pb-0">
            <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-sm font-medium ${color}`}>
                {icon}
            </div>
            <div className="flex-grow min-w-0">
                <p className="text-sm text-gray-900 leading-relaxed">
                    {activity.description}
                </p>
                <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
            </div>
        </div>
    );
};

const RecentActivity = ({ activities }) => {
    const defaultActivities = [
        {
            id: 1,
            type: 'quiz',
            description: 'You completed the "Python Basics" quiz.',
            time: '2 hours ago'
        },
        {
            id: 2,
            type: 'video',
            description: 'You started watching "ReactJS Tutorial".',
            time: '1 day ago'
        },
        {
            id: 3,
            type: 'achievement',
            description: 'You earned the "5-Day Streak" badge!',
            time: '3 days ago'
        },
        {
            id: 4,
            type: 'note',
            description: 'You added a note to "Data Structures" lesson.',
            time: '5 days ago'
        }
    ];

    const activityList = activities || defaultActivities;

    return (
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <h4 className="text-sm font-medium text-gray-900 mb-4">Recent Activity</h4>
            
            {activityList.length === 0 ? (
                <p className="text-sm text-gray-600">No activity yet. Start learning!</p>
            ) : (
                <div className="space-y-3">
                    {activityList.map((activity, index) => (
                        <ActivityItem
                            key={activity.id || index}
                            activity={activity}
                            index={index}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export default RecentActivity;
