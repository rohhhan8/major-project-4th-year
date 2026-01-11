// src/AuthContext.jsx
import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const response = await axios.get('http://localhost:8000/auth/me', {
                    withCredentials: true, // Send cookies with the request
                });
                if (response.status === 200) {
                    setIsAuthenticated(true);
                    setUser(response.data);
                }
            } catch (error) {
                setIsAuthenticated(false);
                setUser(null);
            } finally {
                setLoading(false);
            }
        };

        checkAuth();
    }, []);

    const login = (userData) => {
        setIsAuthenticated(true);
        setUser(userData);
    };

    const logout = async () => {
        try {
            // Call backend to clear the session cookie
            await axios.post('http://localhost:8000/auth/logout', {}, {
                withCredentials: true
            });
        } catch (error) {
            console.log('Logout API error (still clearing local state):', error);
        }
        
        // Clear local state
        setIsAuthenticated(false);
        setUser(null);
        
        // Clear any cached data
        localStorage.clear();
        sessionStorage.clear();
        
        // Force redirect to login page (not just home)
        window.location.href = '/login';
    };

    const value = { isAuthenticated, user, loading, login, logout };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
    return useContext(AuthContext);
};
