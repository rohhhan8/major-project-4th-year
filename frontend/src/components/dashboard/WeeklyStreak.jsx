// src/components/dashboard/WeeklyStreak.jsx
import React from 'react';

const WeeklyStreak = ({ data }) => {
    if (!data) return null;

    const { current, longest } = data;
    const daysOfWeek = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const daysCompleted = [true, true, true, true, true, false, false]; // Mock data

    return (
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
                <h4 className="text-sm font-medium text-gray-600">Weekly Streak</h4>
                <span className="text-2xl">🔥</span>
            </div>
            
            <div className="space-y-4">
                <div>
                    <div className="text-3xl font-semibold mb-1">{current} Days</div>
                    <p className="text-sm text-gray-600">
                        Longest Streak: {longest} days
                    </p>
                </div>

                <div className="grid grid-cols-7 gap-2">
                    {daysCompleted.map((completed, index) => (
                        <div key={index} className="flex flex-col items-center gap-1">
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${
                                completed
                                    ? "bg-gradient-to-br from-blue-500 to-blue-600 text-white"
                                    : "border-2 border-gray-200 text-gray-600"
                            }`}>
                                {String(index + 1).padStart(2, "0")}
                            </div>
                            <span className="text-xs text-gray-500">{daysOfWeek[index]}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default WeeklyStreak;