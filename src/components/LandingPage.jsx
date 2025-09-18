import { useState } from "react";
import AuthModal from './AuthModal';
import FeatureCard from './FeatureCard';
import TestimonialCard from './TestimonialCard';
import { useAuth } from '../hooks/useAuth';
import supabase from '../supabase';

import ThreeLine from '../assets/three-line.svg';

function LandingPage() {
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { user, loading } = useAuth();

  const handleSignOut = async () => {
    await supabase.auth.signOut();
  };

  return (
    <div className="h-screen bg-white text-black font-sans">
      {/* Navigation */}
      <nav className="px-6 py-4 md:px-12 md:py-6">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-black rounded-full"></div>
            <h1 className="text-xl font-bold tracking-tight">EduAI</h1>
          </div>
          
          <div className="hidden md:flex items-center space-x-8">
            <a href="#features" className="hover:underline">Features</a>
            <a href="#about" className="hover:underline">About Us</a>
          </div>

          {/* Mobile Menu Button */}
          <button 
            onClick={() => setIsMenuOpen(!isMenuOpen)} 
            className="md:hidden p-2"
          >
            <img src={ThreeLine} alt="Menu" className="w-8 h-8" />
          </button>

          {/* Desktop Auth Buttons */}
          <div className="hidden md:flex space-x-4">
            {user ? (
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  {user.user_metadata?.avatar_url && (
                    <img 
                      src={user.user_metadata.avatar_url} 
                      alt="Profile" 
                      className="w-8 h-8 rounded-full"
                    />
                  )}
                  <span className="text-sm">
                    {user.user_metadata?.full_name || user.email?.split('@')[0] || 'User'}
                  </span>
                </div>
                <button
                  onClick={handleSignOut}
                  className="px-4 py-2 text-sm border border-black rounded hover:bg-gray-100 transition-colors"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowAuthModal(true)}
                className="px-4 py-2 text-sm bg-black text-white rounded hover:bg-gray-800 transition-colors"
                disabled={loading}
              >
                Get Started
              </button>
            )}
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-4 space-y-4 py-4 text-center">
            <a href="#features" className="block hover:underline">Features</a>
            <a href="#about" className="block hover:underline">About Us</a>
            <div className="pt-4 space-y-2">
              {user ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-center space-x-2 py-2">
                    {user.user_metadata?.avatar_url && (
                      <img 
                        src={user.user_metadata.avatar_url} 
                        alt="Profile" 
                        className="w-6 h-6 rounded-full"
                      />
                    )}
                    <span className="text-sm">
                      {user.user_metadata?.full_name || user.email?.split('@')[0] || 'User'}
                    </span>
                  </div>
                  <button
                    onClick={handleSignOut}
                    className="w-full py-2 text-sm border border-black rounded hover:bg-gray-100 transition-colors"
                  >
                    Sign Out
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="w-full py-2 text-sm bg-black text-white rounded hover:bg-gray-800 transition-colors"
                  disabled={loading}
                >
                  Get Started
                </button>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section with Geometric Shapes */}
      <section className="relative px-6 py-16 md:px-12 md:py-24 text-center overflow-hidden">
        {/* Decorative shapes */}
        <div className="absolute top-10 left-10 w-20 h-20 border border-black rounded-full opacity-10"></div>
        <div className="absolute bottom-20 right-10 w-16 h-16 border border-black opacity-10 rotate-45"></div>
        <div className="absolute top-1/4 right-1/4 w-12 h-12 border border-black opacity-10"></div>
        
        <div className="max-w-4xl mx-auto relative">
          <div className="mb-6">
            <div className="w-24 h-1 bg-black mx-auto mb-4"></div>
            <h2 className="text-3xl md:text-5xl font-bold mb-6 leading-tight tracking-tight">
              AI-Powered Learning<br />Experience
            </h2>
          </div>
          <p className="text-lg md:text-xl mb-8 max-w-2xl mx-auto leading-relaxed">
            Ask intelligent questions, take adaptive exams, and accelerate your education journey with our AI platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {user ? (
              <div className="text-center">
                <p className="text-lg mb-4">Welcome back, {user.user_metadata?.full_name || user.email?.split('@')[0] || 'User'}!</p>
                <button className="px-8 py-4 bg-black text-white rounded-sm font-medium hover:bg-gray-800 transition-colors">
                  Continue Learning
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowAuthModal(true)}
                className="px-8 py-4 bg-black text-white rounded-sm font-medium hover:bg-gray-800 transition-colors"
                disabled={loading}
              >
                Start Learning Now
              </button>
            )}
          </div>
        </div>
      </section>

      {/* Features Section with Custom Shapes */}
      <section id="features" className="px-6 py-16 md:px-12 md:py-24">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div className="w-16 h-1 bg-black mx-auto mb-4"></div>
            <h3 className="text-2xl md:text-3xl font-bold">How It Works</h3>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              title="Ask Questions"
              description="Get instant, intelligent answers to your academic questions from our AI tutor"
              shape="circle"
            />
            <FeatureCard
              title="Take Exams"
              description="Personalized exams that adapt to your knowledge level and learning progress"
              shape="square"
            />
            <FeatureCard
              title="Track Progress"
              description="Monitor your educational journey with detailed analytics and learning insights"
              shape="triangle"
            />
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="px-6 py-16 md:px-12 md:py-24 bg-gray-50">
        <div className="max-w-4xl mx-auto text-center">
          <div className="w-16 h-1 bg-black mx-auto mb-4"></div>
          <h3 className="text-2xl md:text-3xl font-bold mb-12">What Students Say</h3>
          <div className="grid md:grid-cols-2 gap-8">
            <TestimonialCard
              quote="This platform transformed how I study. The AI explanations are incredibly clear."
              author="Sarah, Computer Science Student"
            />
            <TestimonialCard
              quote="The adaptive exams helped me identify my weak areas and improve significantly."
              author="Michael, Medical Student"
            />
          </div>
        </div>
      </section>

      {/* Simplified Footer for Hackathon */}
      <footer className="px-6 py-12 md:px-12 border-t border-gray-200">
        <div className="max-w-6xl mx-auto text-center">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="w-8 h-8 bg-black rounded-full"></div>
            <h4 className="text-lg font-bold">EduAI</h4>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            AI-powered education platform for modern learners.
          </p>
          <p className="text-sm text-gray-600">
            &copy; 2025 EduAI. Built for Hackathon.
          </p>
        </div>
      </footer>

      {/* Auth Modal */}
      {showAuthModal && !user && (
        <AuthModal 
          onClose={() => setShowAuthModal(false)} 
        />
      )}
    </div>
  );
}

export default LandingPage;