import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './components/navbar/Navbar';

const MainLayout = () => {
    return (
        <div className="min-h-screen bg-white">
            <Navbar />
            <main className="pt-32 min-h-screen px-4"> {/* Increased padding for floating navbar */}
                <Outlet /> {/* Child routes will render here */}
            </main>
        </div>
    );
};

export default MainLayout;