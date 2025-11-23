// src/components/dashboard/UpcomingTasks.jsx
import React from 'react';

const TaskItem = ({ task, icon, color }) => {
    const isOverdue = new Date(task.date) < new Date() && !task.completed;

    return (
        <div className={`flex items-start gap-3 p-3 rounded-lg border ${
            task.completed 
                ? 'bg-gray-50 border-gray-100' 
                : isOverdue 
                ? 'bg-red-50 border-red-100' 
                : 'bg-blue-50 border-blue-100 hover:border-blue-200'
        } transition-colors`}>
            <div className={`mt-1 flex-shrink-0 w-2 h-2 rounded-full ${color}`}></div>
            <div className="flex-grow min-w-0">
                <p className={`text-sm font-medium ${
                    task.completed ? 'line-through text-gray-500' : 'text-gray-900'
                }`}>
                    {task.title}
                </p>
                <p className="text-xs text-gray-600 mt-1">
                    {new Date(task.date).toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric' 
                    })}
                    {isOverdue && !task.completed && (
                        <span className="ml-2 text-red-600 font-medium">Overdue</span>
                    )}
                </p>
            </div>
        </div>
    );
};

const UpcomingTasks = ({ tasks }) => {
    const defaultTasks = [
        { id: 1, title: 'React Quiz', date: '2025-11-15', completed: false },
        { id: 2, title: 'Watch FastAPI Tutorial', date: '2025-11-18', completed: false },
        { id: 3, title: 'Submit Python Project', date: '2025-11-20', completed: true }
    ];

    const taskList = tasks || defaultTasks;
    const colorClasses = ['bg-blue-600', 'bg-green-600', 'bg-purple-600', 'bg-orange-600'];

    return (
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <h4 className="text-sm font-medium text-gray-900 mb-4">Upcoming Tasks</h4>
            
            {taskList.length === 0 ? (
                <p className="text-sm text-gray-600">No tasks. Great job!</p>
            ) : (
                <div className="space-y-2">
                    {taskList.map((task, index) => (
                        <TaskItem
                            key={task.id || index}
                            task={task}
                            color={colorClasses[index % colorClasses.length]}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export default UpcomingTasks;
