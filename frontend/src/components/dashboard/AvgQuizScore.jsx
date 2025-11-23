// src/components/dashboard/AvgQuizScore.jsx
import React from 'react';

const AvgQuizScore = ({ data }) => {
    if (!data) return null;

    const { avg, highest, lowest, change } = data;
    const isPositive = change >= 0;

    return (
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
                <h4 className="text-sm font-medium text-gray-600">Avg Quiz Score</h4>
                <div className={`flex items-center gap-1 text-sm font-medium ${
                    isPositive ? 'text-green-600' : 'text-red-600'
                }`}>
                    <svg 
                        className={`w-4 h-4 transition-transform ${isPositive ? '' : 'rotate-180'}`}
                        fill="currentColor"
                        viewBox="0 0 20 20"
                    >
                        <path fillRule="evenodd" d="M10 14a.75.75 0 01-.75-.75V6.56l-2.22 2.22a.75.75 0 11-1.06-1.06l3.5-3.5a.75.75 0 011.06 0l3.5 3.5a.75.75 0 01-1.06 1.06L10.75 6.56V13.25A.75.75 0 0110 14z" clipRule="evenodd" />
                    </svg>
                    <span>{Math.abs(change)}%</span>
                </div>
            </div>

            <div className="text-3xl font-semibold text-gray-900 mb-4">{avg}%</div>

            <div className="space-y-3">
                <div>
                    <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium text-gray-600">Highest Score</span>
                        <span className="text-sm font-semibold text-blue-600">{highest}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                        <div 
                            className="bg-blue-600 h-1.5 rounded-full transition-all"
                            style={{ width: `${highest}%` }}
                        ></div>
                    </div>
                </div>

                <div>
                    <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium text-gray-600">Lowest Score</span>
                        <span className="text-sm font-semibold text-orange-600">{lowest}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                        <div 
                            className="bg-orange-500 h-1.5 rounded-full transition-all"
                            style={{ width: `${lowest}%` }}
                        ></div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AvgQuizScore;
