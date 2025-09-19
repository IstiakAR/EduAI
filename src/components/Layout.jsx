import { useState } from "react";
import { useAuth } from '../hooks/useAuth';
import supabase from '../supabase';
import Avatar from './Avatar';
import ThreeLine from '../assets/three-line.svg';
import AuthModal from "./AuthModal";

function Layout({ children, showHero = false, heroContent = null, onNavigate }) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { user, loading } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  const handleSignOut = async () => {
    await supabase.auth.signOut();
  };

  const handleNavClick = (page) => {
    if (onNavigate) {
      onNavigate(page);
    }
  };

  return (
    <div className="min-h-screen bg-white text-black font-sans">
      {/* Geometric Background Decorations */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-10 left-10 w-20 h-20 border border-black rounded-full opacity-10"></div>
        <div className="absolute bottom-20 right-10 w-16 h-16 border border-black opacity-10 rotate-45"></div>
        <div className="absolute top-1/4 right-1/4 w-12 h-12 border border-black opacity-10"></div>
        <div className="absolute top-1/2 left-1/3 w-8 h-8 border border-black opacity-5 rotate-12"></div>
        <div className="absolute bottom-1/3 left-20 w-14 h-14 border border-black rounded-full opacity-5"></div>
        <div className="absolute top-3/4 right-1/3 w-10 h-10 border border-black opacity-5"></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 px-6 py-4 md:px-12 md:py-6">
        <div className="flex justify-between items-center md:grid md:grid-cols-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-black rounded-full"></div>
            <h1 className="text-xl font-bold tracking-tight">EduAI</h1>
          </div>
          
          <div className="hidden md:flex items-center justify-center space-x-8">
            <a href="/" className="hover:underline">Home</a>
            <a href="/dashboard" className="hover:underline">Dashboard</a>
            <a href="/#features" className="hover:underline">Features</a>
            <a href="/#about" className="hover:underline">About Us</a>
          </div>

          <div className="flex justify-end">
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
                    <Avatar 
                      src={user.user_metadata?.avatar_url}
                      alt={`${user.user_metadata?.full_name || user.email?.split('@')[0] || 'User'}'s avatar`}
                      size="w-8 h-8"
                      fallbackText={(user.user_metadata?.full_name || user.email?.split('@')[0] || 'U')[0].toUpperCase()}
                    />
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
                >
                  Get Started
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-4 space-y-4 py-4 text-center">
            <a href="/" className="block hover:underline">Home</a>
            <a href="/dashboard" className="block hover:underline">Dashboard</a>
            <a href="#features" className="block hover:underline">Features</a>
            <a href="#about" className="block hover:underline">About Us</a>
            <div className="pt-4 space-y-2">
              {user ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-center space-x-2 py-2">
                    <Avatar 
                      src={user.user_metadata?.avatar_url}
                      alt={`${user.user_metadata?.full_name || user.email?.split('@')[0] || 'User'}'s avatar`}
                      size="w-6 h-6"
                      fallbackText={(user.user_metadata?.full_name || user.email?.split('@')[0] || 'U')[0].toUpperCase()}
                    />
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
                <a
                  href="/"
                  className="block w-full py-2 text-sm bg-black text-white rounded hover:bg-gray-800 transition-colors"
                >
                  Get Started
                </a>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Optional Hero Section */}
      {showHero && heroContent && (
        <section className="relative px-6 py-16 md:px-12 md:py-24 text-center overflow-hidden">
          <div className="max-w-4xl mx-auto relative z-10">
            {heroContent}
          </div>
        </section>
      )}

      {/* Main Content */}
      <main className="relative z-10">
        {children}
      </main>
      {showAuthModal && !user && (
        <AuthModal 
          onClose={() => setShowAuthModal(false)} 
        />
      )}
    </div>
  );
}

export default Layout;