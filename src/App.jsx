import React, { useState } from 'react';
import { useAuth } from './hooks/useAuth';
import LandingPage from './components/LandingPage';
import ChatPage from './components/ChatPage';
import Dashboard from './components/Dashboard';
import AuthModal from './components/AuthModal';
import './index.css';

function AppContent() {
  const [currentPage, setCurrentPage] = useState('landing');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const { user, loading } = useAuth();

  console.log('App state:', { currentPage, user: user?.id, loading });

  const handleGetStarted = () => {
    console.log('Get started clicked');
    if (user) {
      setCurrentPage('dashboard');
    } else {
      setCurrentPage('chat');
    }
  };

  const handleSignIn = () => {
    console.log('Sign in clicked');
    setShowAuthModal(true);
  };

  const handleAuthSuccess = () => {
    console.log('Auth success');
    setShowAuthModal(false);
    setCurrentPage('dashboard');
  };

  const handleNavigate = (page) => {
    console.log('Navigating to:', page);
    setCurrentPage(page);
  };

  if (loading) {
    console.log('App is loading...');
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      {currentPage === 'landing' ? (
        <LandingPage 
          onGetStarted={handleGetStarted}
          onSignIn={handleSignIn}
        />
      ) : currentPage === 'dashboard' ? (
        <Dashboard onNavigate={handleNavigate} />
      ) : (
        <ChatPage onNavigate={handleNavigate} />
      )}
      
      {showAuthModal && (
        <AuthModal 
          onClose={() => setShowAuthModal(false)}
          onSuccess={handleAuthSuccess}
        />
      )}
    </div>
  );
}

export default AppContent;
