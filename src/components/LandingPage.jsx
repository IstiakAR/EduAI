import { useState } from "react";
import AuthModal from "./AuthModal";
import FeatureCard from "./FeatureCard";
import TestimonialCard from "./TestimonialCard";
import TeamMember from "./TeamMember";
import Layout from "./Layout";
import { useAuth } from "../hooks/useAuth";

function LandingPage() {
  const [showAuthModal, setShowAuthModal] = useState(false);
  const { user } = useAuth();

  const heroContent = (
    <>
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
            <button className="px-8 py-4 bg-black text-white rounded-sm font-medium hover:bg-gray-800 transition-colors" onClick={() => window.location.href = "/chat"}>
              Countine Learning
            </button>
          </div>
        ) : (
          <button
            onClick={() => setShowAuthModal(true)}
            className="px-8 py-4 bg-black text-white rounded-sm font-medium hover:bg-gray-800 transition-colors"
          >
            Start Learning Now
          </button>
        )}
      </div>
    </>
  );

  return (
    <Layout showHero={true} heroContent={heroContent}>
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

      <section id="about" className="px-6 py-16 md:px-12 md:py-24">
        <div className="max-w-4xl mx-auto text-center">
          <div className="w-16 h-1 bg-black mx-auto mb-4"></div>
          <h3 className="text-2xl md:text-3xl font-bold mb-12">About Us</h3>
          <p className="text-lg text-gray-600 mb-12 max-w-2xl mx-auto">
            We are a team of passionate developers building the future of AI-powered education.
          </p>
          
          <div className="grid md:grid-cols-4 gap-8">
            <TeamMember 
              name="Istiak Ahammed Rhyme"
              initial="I"
              gradientColors="from-yellow-400 to-red-500"
              githubUrl="https://github.com/IstiakAR"
              linkedinUrl="https://linkedin.com/in/istiak-rhyme"
              facebookUrl="https://facebook.com/istiak.rhyme"
            />
                        
            <TeamMember 
              name="Jubayer Ahmed Sojib"
              initial="J"
              gradientColors="from-green-400 to-blue-500"
              githubUrl="#"
              linkedinUrl="#"
              facebookUrl="https://facebook.com/suraya.mim"
            />    
            <TeamMember 
              name="Suraya Jannat Mim"
              initial="S"
              gradientColors="from-pink-400 to-blue-500"
              githubUrl="#"
              linkedinUrl="#"
              facebookUrl="https://facebook.com/suraya.mim"
            />
            <TeamMember 
              name="Md. Akram Khan"
              initial="A"
              gradientColors="from-yellow-400 to-violet-500"
              githubUrl="#"
              linkedinUrl="#"
              facebookUrl="https://facebook.com/akram.khan"
            />
          </div>
        </div>
      </section>

      {showAuthModal && !user && (
        <AuthModal 
          onClose={() => setShowAuthModal(false)} 
        />
      )}

      {/* Footer */}
      <footer className="relative z-10 px-6 py-12 md:px-12 border-t border-gray-200 mt-16">
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
    </Layout>
    
  );
}

export default LandingPage;
