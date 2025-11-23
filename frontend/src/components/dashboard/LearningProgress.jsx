// src/components/dashboard/LearningProgress.jsx
import React from 'react';

const ProgressBar = ({ label, value, color }) => (
    <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-900">{label}</span>
            <span className="text-sm font-semibold text-gray-600">{value}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
                className={`${color} h-2 rounded-full transition-all`}
                style={{ width: `${value}%` }}
            ></div>
        </div>
    </div>
);

const LearningProgress = ({ progress }) => {
    // Support both single progress value and multiple subjects
    if (typeof progress === 'number') {
        return (
            <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
                <h4 className="text-sm font-medium text-gray-900 mb-4">Learning Progress</h4>
                <ProgressBar label="Overall" value={progress} color="bg-blue-600" />
                <div className="text-xs text-gray-600 text-right">
                    {progress}% Complete
                </div>
            </div>
        );
    }

    // Support object with multiple subjects
    const subjects = progress || {
        Python: 75,
        "Web Development": 60,
        "Data Science": 45,
        "Mobile Apps": 30
    };

    const colorMap = {
        0: 'bg-blue-600',
        1: 'bg-green-600',
        2: 'bg-purple-600',
        3: 'bg-orange-600'
    };

    return (
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <h4 className="text-sm font-medium text-gray-900 mb-4">Learning Progress</h4>
            <div className="space-y-3">
                {Object.entries(subjects).map(([label, value], index) => (
                    <ProgressBar
                        key={label}
                        label={label}
                        value={value}
                        color={colorMap[index % 4]}
                    />
                ))}
            </div>
        </div>
    );
};

export default LearningProgress;
