import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './components/navbar/Navbar';

const MainLayout = () => {
    return (
        <div className="min-h-screen bg-gray-50">
            <Navbar />
            <main className="pt-16"> {/* Add padding-top to avoid content overlap */}
                <Outlet /> {/* Child routes will render here */}
            </main>
        </div>
    );
};

export default MainLayout;