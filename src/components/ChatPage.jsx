import React, { useState } from 'react';
import ChatIcon from '../assets/chat.svg';
import { apiService } from '../services/apiService';

function ChatPage() {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const [examStarted, setExamStarted] = useState(true);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  
  const [examPanelWidth, setExamPanelWidth] = useState(320);
  const [isResizing, setIsResizing] = useState(false);
  
  // Sample math exam questions to match the design
  const examQuestions = [
    {
      id: 1,
      type: "mcq",
      question: "Solve for x: 2x + 5 = 15",
      options: ["x = 5", "x = 7.5", "x = 10"]
    },
    {
      id: 2,
      type: "mcq", 
      question: "What is the derivative of x²?",
      options: ["2x", "x", "2x²"]
    }
  ];

  // Chat messages - now dynamic
  const [messages, setMessages] = useState([]);
  
  const currentQuestion = examQuestions[currentQuestionIndex];

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMessage = {
      id: Date.now(),
      from: "user",
      text: input.trim()
    };
    
    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input.trim();
    setInput('');
    setIsLoading(true);
    
    try {
      // Get AI response
      const aiResponse = await apiService.sendMessage(currentInput);
      
      // Add AI response
      const aiMessage = {
        id: Date.now() + 1,
        from: "ai",
        text: aiResponse
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
    } catch (error) {
      console.error('Failed to get AI response:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        from: "ai",
        text: "Sorry, I'm having trouble connecting to the AI service. Please try again later."
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswerChange = (value) => {
    setAnswers((prev) => ({ ...prev, [currentQuestion.id]: value }));
  };

  const handleMouseDown = (e) => {
    setIsResizing(true);
    e.preventDefault();
  };

  const handleMouseMove = (e) => {
    if (!isResizing) return;
    
    const windowWidth = window.innerWidth;
    const newWidth = windowWidth - e.clientX - 16;
    
    const constrainedWidth = Math.min(Math.max(newWidth, 280), 1000);
    setExamPanelWidth(constrainedWidth);
  };

  const handleMouseUp = () => {
    setIsResizing(false);
  };

  React.useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing]);

  return (
    <div className="h-screen bg-gray-100 flex">
      {/* Left Sidebar - Navigation */}
      <div className="w-16 bg-gray-200 flex flex-col items-center p-6">
        {/* Navigation Icons */}
        <div className="space-y-6">
          {/* Add New/Plus Icon */}
          <button className="w-8 h-8 bg-black rounded-full flex items-center justify-center text-white text-lg font-bold">
            +
          </button>
          
          {/* Home Icon */}
          <button className="p-2 hover:bg-gray-300 rounded-lg transition-colors">
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
          </button>
          
          {/* Chat Icon */}
          <button className="p-2 hover:bg-gray-300 rounded-lg transition-colors">
            <img src={ChatIcon} alt="Chat Icon" className="w-5 h-5 text-gray-600" />
          </button>
          
        </div>
        
        {/* Bottom Icons */}
        <div className="mt-auto space-y-4">
          {/* Settings Icon */}
          <button className="p-2 hover:bg-gray-300 rounded-lg transition-colors">
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
          
          {/* Help/Question Icon */}
          <button className="p-2 hover:bg-gray-300 rounded-lg transition-colors">
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
          
          {/* User Avatar */}
          <div className="w-8 h-8 bg-orange-400 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-medium">U</span>
          </div>
        </div>
      </div>

      {/* Center Panel - AI Chat */}
      <div className="bg-white flex flex-col" style={{ width: `calc(100% - 64px - ${examPanelWidth}px)` }}>
        {/* Chat Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-bold">AI</span>
            </div>
            <h2 className="text-lg font-medium text-gray-900">AI</h2>
          </div>
        </div>
        
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map(({ id, from, text }) => (
            <div
              key={id}
              className={`flex ${from === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[75%] px-4 py-3 rounded-2xl ${
                  from === "user"
                    ? "bg-black text-white"
                    : "bg-gray-100 text-gray-900"
                }`}
              >
                <p className="text-sm leading-relaxed">{text}</p>
              </div>
            </div>
          ))}
          
          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-900 px-4 py-3 rounded-2xl">
                <div className="flex items-center space-x-2">
                  <div className="animate-pulse">🤖</div>
                  <span className="text-sm">AI is thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Chat Input */}
        <div className="border-t border-gray-200 p-6">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              sendMessage();
            }}
            className="flex gap-3 items-center"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={isLoading ? "AI is thinking..." : "Type your message..."}
              disabled={isLoading}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:border-gray-400 text-sm disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="p-3 text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </form>
        </div>
      </div>

      {/* Resize Handle */}
      <div
        className="w-1 bg-gray-300 cursor-col-resize hover:bg-gray-400 transition-colors relative group"
        onMouseDown={handleMouseDown}
      >
        <div className="absolute inset-y-0 left-1/2 transform -translate-x-1/2 w-3 -ml-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <div className="h-full w-full bg-gray-500 rounded-full" />
        </div>
      </div>

      {/* Right Panel - Exam Section */}
      <div className="bg-gray-50 border-l border-gray-200 flex flex-col" style={{ width: `${examPanelWidth}px` }}>
        {/* Exam Header */}
        <div className="px-6 py-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">Math Exam</h2>
            <div className="flex gap-2">
              <button className="p-2 hover:bg-gray-200 rounded-lg transition-colors">
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <button className="p-2 hover:bg-gray-200 rounded-lg transition-colors">
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </button>
              <button className="p-2 hover:bg-gray-200 rounded-lg transition-colors">
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Exam Content */}
        <div className="flex-1 p-6">
          <div className="space-y-6">
            {/* Question Header */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Question 1:</h3>
              <p className="text-gray-700 text-lg mb-6">{currentQuestion.question}</p>
            </div>

            {/* Options */}
            <div className="space-y-4">
              <h4 className="text-base font-medium text-gray-900 mb-4">Options:</h4>
              {currentQuestion.options.map((option, index) => (
                <label 
                  key={index} 
                  className="flex items-center space-x-3 cursor-pointer p-3 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <input
                    type="radio"
                    name={`question-${currentQuestion.id}`}
                    value={option}
                    checked={answers[currentQuestion.id] === option}
                    onChange={() => handleAnswerChange(option)}
                    className="w-4 h-4 text-gray-600 border-2 border-gray-300 focus:ring-gray-500"
                  />
                  <span className="text-gray-700 text-base">{option}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="p-6 border-t border-gray-200">
          <button className="w-full bg-black text-white py-3 px-6 rounded-lg font-medium hover:bg-gray-800 transition-colors">
            Submit Answer
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatPage;