// src/pages/LoginPage.jsx
import React from 'react';

const LoginPage = () => {
    const handleLogin = () => {
        // Redirect to the backend login URL
        window.location.href = 'http://localhost:8000/auth/login';
    };

    return (
        <div className="flex items-center justify-center h-screen bg-white">
            <div className="text-center">
                <h1 className="text-4xl font-bold mb-8">Adaptive Learning Platform</h1>
                <button
                    onClick={handleLogin}
                    className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg shadow-lg"
                >
                    Sign in with Google
                </button>
            </div>
        </div>
    );
};

export default LoginPage;
