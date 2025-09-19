import React, { useState, useEffect } from 'react';
import ChatIcon from '../assets/chat.svg';
import { apiService } from '../services/apiService';
import { useAuth, useUserId } from '../hooks/useAuth';

function ChatPage({ onNavigate }) {
  const { user } = useAuth();
  const userId = useUserId();
  
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showNewChatModal, setShowNewChatModal] = useState(false);
  const [newChatSubject, setNewChatSubject] = useState('');
  const [currentChatSubject, setCurrentChatSubject] = useState('');
  
  // Chat management
  const [currentChatId, setCurrentChatId] = useState(null);
  const [userChats, setUserChats] = useState([]);
  const [messages, setMessages] = useState([]);
  
  // Exam mode state
  const [isExamMode, setIsExamMode] = useState(false);
  const [showExamForm, setShowExamForm] = useState(false);
  const [currentExam, setCurrentExam] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [examAnswers, setExamAnswers] = useState([]);
  const [examResults, setExamResults] = useState(null);
  const [userExams, setUserExams] = useState([]);
  const [showExamHistory, setShowExamHistory] = useState(false);
  
  // Exam form state
  const [examForm, setExamForm] = useState({
    title: '',
    subject: '',
    exam_type: 'mcq',
    num_questions: 10,
    difficulty: 'medium',
    topic: ''
  });
  
  const [examPanelWidth, setExamPanelWidth] = useState(720);
  const [isResizing, setIsResizing] = useState(false);

  function cleanResponse(text) {
    // Clean various markdown and formatting elements
    return text
      .replace(/\*\*/g, "")           // Remove bold markers
      .replace(/\*/g, "")             // Remove italic markers
      .replace(/^\* .*$/gm, "")       // Remove bullet points
      .replace(/^#{1,6}\s*/gm, "")    // Remove headers
      .replace(/```[\s\S]*?```/g, "") // Remove code blocks
      .replace(/`([^`]+)`/g, "$1")    // Remove inline code markers
      .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1") // Remove links but keep text
      .replace(/^\s*[-+*]\s+/gm, "")  // Remove list markers
      .replace(/^\s*\d+\.\s+/gm, "")  // Remove numbered list markers
      .replace(/^\s*>\s*/gm, "")      // Remove blockquotes
      .replace(/\n{3,}/g, "\n\n")     // Reduce multiple newlines to double
      .replace(/^\s+|\s+$/g, "")      // Trim whitespace
      .replace(/\s{2,}/g, " ");       // Reduce multiple spaces to single
  }

  useEffect(() => {
    console.log('ChatPage useEffect - userId:', userId);
    if (userId) {
      loadUserChats();
      loadUserExams();
    }
  }, [userId]);

  const loadUserChats = async () => {
    try {
      console.log('=== LOADING USER CHATS ===');
      console.log('Loading chats for userId:', userId);
      
      if (!userId) {
        console.warn('No userId available, skipping chat loading');
        return;
      }
      
      const chats = await apiService.getUserChats(userId);
      console.log('Raw chats response:', chats);
      console.log('Chats array length:', chats?.length);
      
      if (chats && chats.length > 0) {
        console.log('First chat structure:', chats[0]);
        console.log('Chat data keys:', Object.keys(chats[0]));
      }
      
      setUserChats(chats || []);
      console.log('=== CHAT LOADING COMPLETE ===');
    } catch (error) {
      console.error('Failed to load user chats:', error);
      setUserChats([]); // Set empty array on error
    }
  };

  const loadUserExams = async () => {
    try {
      console.log('=== LOADING USER EXAMS ===');
      console.log('Loading exams for userId:', userId);
      console.log('UserId type:', typeof userId);
      console.log('UserId length:', userId?.length);
      
      if (!userId) {
        console.warn('No userId available, skipping exam loading');
        return;
      }
      
      console.log('Calling apiService.getUserExams...');
      const exams = await apiService.getUserExams(userId);
      console.log('Raw exams response:', exams);
      console.log('Exams array length:', exams?.length);
      console.log('Setting userExams state...');
      setUserExams(exams);
      console.log('=== EXAM LOADING COMPLETE ===');
    } catch (error) {
      console.error('Failed to load user exams:', error);
      console.error('Error details:', error.message, error.stack);
      setUserExams([]); // Set empty array on error to prevent UI issues
    }
  };

    const saveCurrentChat = async () => {
    console.log('saveCurrentChat called - currentChatId:', currentChatId, 'userId:', userId, 'messages.length:', messages.length);
    if (!currentChatId || !userId || messages.length === 0) return;
    
    try {
      console.log('Saving chat to database...');
      await apiService.updateChat(currentChatId, userId, messages, {
        subject: currentChatSubject,
        lastActivity: new Date().toISOString()
      });
      console.log('Chat saved successfully');
    } catch (error) {
      console.error('Failed to save chat:', error);
    }
  };

  const loadChat = async (chat) => {
    try {
      console.log('=== LOADING CHAT ===');
      console.log('Chat object:', chat);
      console.log('Chat keys:', Object.keys(chat));
      
      // Save current chat before switching
      if (currentChatId) {
        await saveCurrentChat();
      }
      
      console.log('Setting chat ID:', chat.chat_id);
      console.log('Setting chat subject:', chat.subject);
      console.log('Chat data:', chat.chat_data);
      console.log('Messages from chat data:', chat.chat_data?.messages);
      
      setCurrentChatId(chat.chat_id);
      setCurrentChatSubject(chat.subject || 'Untitled Chat');
      
      const chatMessages = chat.chat_data?.messages || [];
      console.log('Setting messages:', chatMessages.length, 'messages');
      setMessages(chatMessages);
      
      console.log('=== CHAT LOADING COMPLETE ===');
    } catch (error) {
      console.error('Failed to load chat:', error);
    }
  };

  // Auto-save chat when messages change
  useEffect(() => {
    if (currentChatId && messages.length > 0) {
      const timeoutId = setTimeout(() => {
        saveCurrentChat();
      }, 2000); // Save after 2 seconds of inactivity
      
      return () => clearTimeout(timeoutId);
    }
  }, [messages, currentChatId]);

  const handleNewChat = () => {
    setShowNewChatModal(true);
  };

  const createNewChat = async () => {
    console.log('createNewChat called - userId:', userId, 'subject:', newChatSubject.trim());
    if (newChatSubject.trim() && userId) {
      try {
        // Save current chat before creating new one
        if (currentChatId) {
          await saveCurrentChat();
        }
        
        console.log('Creating new chat in database...');
        // Create new chat in database
        const newChat = await apiService.createChat(
          userId,
          `${newChatSubject.trim()} Chat`,
          newChatSubject.trim()
        );
        
        console.log('New chat created:', newChat);
        setCurrentChatId(newChat.chat_id);
        setCurrentChatSubject(newChatSubject.trim());
        setMessages([]);
        setNewChatSubject('');
        setShowNewChatModal(false);
        
        // Add a welcome message based on the subject
        const welcomeMessage = {
          id: Date.now(),
          from: "ai",
          text: `Hello! I'm ready to help you with ${newChatSubject.trim()}. What would you like to know?`,
          timestamp: new Date().toISOString()
        };
        setMessages([welcomeMessage]);
        
        // Refresh chat list
        await loadUserChats();
        
      } catch (error) {
        console.error('Failed to create new chat:', error);
        // Fallback to local storage for demo
        setCurrentChatSubject(newChatSubject.trim());
        setMessages([]);
        setNewChatSubject('');
        setShowNewChatModal(false);
        
        const welcomeMessage = {
          id: Date.now(),
          from: "ai",
          text: `Hello! I'm ready to help you with ${newChatSubject.trim()}. What would you like to know?`,
          timestamp: new Date().toISOString()
        };
        setMessages([welcomeMessage]);
      }
    }
  };

  const cancelNewChat = () => {
    setNewChatSubject('');
    setShowNewChatModal(false);
  };

  // Exam functionality
  const toggleExamMode = () => {
    setIsExamMode(!isExamMode);
    if (!isExamMode) {
      setShowExamForm(true);
    } else {
      // Reset exam state when exiting exam mode
      setCurrentExam(null);
      setExamAnswers([]);
      setExamResults(null);
      setCurrentQuestionIndex(0);
      setShowExamForm(false);
    }
  };

  const handleExamFormChange = (field, value) => {
    setExamForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

    const generateExam = async () => {
    if (!examForm.title.trim() || !examForm.subject.trim() || !userId) {
      alert('Please fill in all required fields');
      return;
    }

    setIsLoading(true);
    try {
      const examData = {
        user_id: userId,
        chat_id: currentChatId,
        title: examForm.title,
        subject: examForm.subject,
        exam_type: examForm.exam_type,
        num_questions: examForm.num_questions,
        difficulty: examForm.difficulty,
        topic: examForm.topic || null
      };

      console.log('Generating exam with data:', examData);
      const generatedExam = await apiService.generateExam(examData);
      
      setCurrentExam(generatedExam);
      setShowExamForm(false);
      setCurrentQuestionIndex(0);
      setExamAnswers([]);
      setExamResults(null);
      
      // Refresh exam list
      await loadUserExams();
      
      console.log('Exam generated successfully:', generatedExam);
    } catch (error) {
      console.error('Failed to generate exam:', error);
      alert('Failed to generate exam. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswerSelect = (questionId, answer) => {
    const newAnswers = [...examAnswers];
    const existingIndex = newAnswers.findIndex(a => a.question_id === questionId);
    
    if (existingIndex >= 0) {
      newAnswers[existingIndex] = { question_id: questionId, answer };
    } else {
      newAnswers.push({ question_id: questionId, answer });
    }
    
    setExamAnswers(newAnswers);
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < currentExam.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const previousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const submitExam = async () => {
    if (!currentExam || !userId) return;

    if (examAnswers.length < currentExam.questions.length) {
      const confirm = window.confirm(
        `You have only answered ${examAnswers.length} out of ${currentExam.questions.length} questions. Submit anyway?`
      );
      if (!confirm) return;
    }

    setIsLoading(true);
    try {
      console.log('Submitting exam:', { examId: currentExam.exam_id, answers: examAnswers });
      const results = await apiService.submitExam(currentExam.exam_id, userId, examAnswers);
      
      setExamResults(results);
      
      // Add exam results to chat messages
      await addExamResultsToChat(results, currentExam);
      
      // Refresh exam list to show updated status
      await loadUserExams();
      
      console.log('Exam submitted successfully:', results);
    } catch (error) {
      console.error('Failed to submit exam:', error);
      alert('Failed to submit exam. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const addExamResultsToChat = async (results, examData = null) => {
    console.log('=== ADD EXAM RESULTS TO CHAT ===');
    console.log('Results parameter:', results);
    console.log('ExamData parameter:', examData);
    console.log('Current exam state:', currentExam);
    
    // Use the passed examData or fall back to currentExam state
    const exam = examData || currentExam;
    
    if (!exam || !results) {
      console.log('Missing exam or results, returning early');
      console.log('exam:', !!exam);
      console.log('results:', !!results);
      return;
    }

    console.log('Using exam data:', exam.title, exam.exam_type);
    console.log('Creating summary message...');
    
    // Create exam summary message
    const summaryMessage = {
      id: Date.now(),
      from: "ai",
      text: `🎯 **Exam Completed: ${exam.title}**\n\n📊 **Results:**\n• Score: ${results.score}/${results.max_score}\n• Percentage: ${results.percentage.toFixed(1)}%\n• Exam Type: ${(exam.exam_type || 'mcq').toUpperCase()}\n\n📝 **Detailed Review:**`,
      timestamp: new Date().toISOString()
    };

    console.log('Summary message created:', summaryMessage);

    // Create detailed review messages for each question
    const reviewMessages = [];
    
    console.log('Checking for question results:', results.results?.question_results);
    if (results.results?.question_results) {
      console.log('Processing', results.results.question_results.length, 'question results');
      results.results.question_results.forEach((result, index) => {
        let reviewText = '';
        
        if ((exam.exam_type || 'mcq') === 'mcq') {
          // MCQ Review
          const isCorrect = result.is_correct;
          const statusIcon = isCorrect ? '✅' : '❌';
          
          reviewText = `${statusIcon} **Question ${index + 1}:**\n${result.question}\n\n` +
                      `**Your Answer:** ${result.user_answer || 'No answer'}\n` +
                      `**Correct Answer:** ${result.correct_answer}\n` +
                      `**Status:** ${isCorrect ? 'Correct' : 'Incorrect'}`;
          
          if (result.explanation) {
            reviewText += `\n\n**Explanation:** ${result.explanation}`;
          }
        } else {
          // Written Review
          const score = result.score || 0;
          const maxPoints = result.max_points || 10;
          const percentage = maxPoints > 0 ? (score / maxPoints * 100).toFixed(1) : 0;
          
          reviewText = `📝 **Question ${index + 1}:** (${score}/${maxPoints} points - ${percentage}%)\n${result.question}\n\n` +
                      `**Your Answer:** ${result.user_answer || 'No answer provided'}\n`;
          
          if (result.feedback) {
            reviewText += `\n**Feedback:** ${result.feedback}`;
          }
          
          if (result.strengths) {
            reviewText += `\n\n**Strengths:** ${result.strengths}`;
          }
          
          if (result.improvements) {
            reviewText += `\n\n**Areas for Improvement:** ${result.improvements}`;
          }
        }
        
        reviewMessages.push({
          id: Date.now() + index + 1,
          from: "ai",
          text: reviewText,
          timestamp: new Date().toISOString()
        });
      });
    } else {
      console.log('No question_results found in results.results');
    }

    console.log('Review messages created:', reviewMessages.length);

    // Add all messages to chat
    const allNewMessages = [summaryMessage, ...reviewMessages];
    console.log('All new messages to add:', allNewMessages.length);
    console.log('Current messages before adding:', messages.length);
    
    setMessages(prevMessages => {
      const updatedMessages = [...prevMessages, ...allNewMessages];
      console.log('Updated messages array length:', updatedMessages.length);
      return updatedMessages;
    });

    // Save to database if we have a current chat
    if (currentChatId) {
      console.log('Saving to database, chat ID:', currentChatId);
      try {
        const updatedMessages = [...messages, ...allNewMessages];
        await apiService.updateChat(currentChatId, userId, updatedMessages, {
          subject: currentChatSubject,
          lastActivity: new Date().toISOString()
        });
        console.log('Successfully saved exam results to chat');
      } catch (error) {
        console.error('Failed to save exam results to chat:', error);
      }
    } else {
      console.log('No currentChatId, skipping database save');
    }
    
    console.log('=== ADD EXAM RESULTS TO CHAT COMPLETE ===');
  };

  const restartExam = () => {
    setCurrentExam(null);
    setExamAnswers([]);
    setExamResults(null);
    setCurrentQuestionIndex(0);
    setShowExamForm(true);
  };

  const loadExamFromHistory = async (examId) => {
    try {
      console.log('=== LOADING EXAM FROM HISTORY ===');
      console.log('Exam ID:', examId);
      
      const exam = await apiService.getExamById(examId);
      console.log('Loaded exam:', exam);
      console.log('Exam status:', exam.status);
      console.log('Exam data:', exam.exam_data);
      
      if (exam.status === 'completed') {
        console.log('Processing completed exam...');
        
        // Show completed exam results
        const results = {
          exam_id: exam.exam_id,
          score: exam.exam_data?.results?.score || 0,
          max_score: exam.max_score || exam.exam_data?.max_score || 0,
          percentage: exam.exam_data?.results?.percentage || 0,
          results: exam.exam_data?.results || {}
        };
        
        console.log('Constructed results object:', results);
        console.log('Current exam before setting:', currentExam);
        
        setCurrentExam(exam);
        setExamResults(results);
        setExamAnswers(exam.exam_data?.user_answers || []);
        
        console.log('About to call addExamResultsToChat...');
        // Add exam review to chat - pass the exam directly instead of relying on state
        await addExamResultsToChat(results, exam);
        console.log('addExamResultsToChat completed');
        
      } else {
        console.log('Processing in-progress exam...');
        // Resume in-progress exam
        setCurrentExam(exam);
        setExamAnswers(exam.exam_data?.user_answers || []);
        setExamResults(null);
        setCurrentQuestionIndex(0);
      }
      
      setShowExamHistory(false);
      setShowExamForm(false);
      console.log('=== EXAM LOADING COMPLETE ===');
    } catch (error) {
      console.error('Failed to load exam:', error);
      console.error('Error details:', error.message, error.stack);
      alert('Failed to load exam. Please try again.');
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMessage = {
      id: Date.now(),
      from: "user",
      text: input.trim(),
      timestamp: new Date().toISOString()
    };
    
    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input.trim();
    setInput('');
    setIsLoading(true);
    
    try {
      // Get AI response
      const aiResponse = await apiService.sendMessage(currentInput);
      
      // Clean the AI response to remove formatting
      const cleanedResponse = cleanResponse(aiResponse);
      
      // Add AI response
      const aiMessage = {
        id: Date.now() + 1,
        from: "ai",
        text: cleanedResponse,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
    } catch (error) {
      console.error('Failed to get AI response:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        from: "ai",
        text: "Sorry, I'm having trouble connecting to the AI service. Please try again later.",
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswerChange = (value) => {
    setAnswers((prev) => ({ ...prev, [currentQuestion.id]: value }));
  };

  const createExamForCurrentChat = async () => {
    if (!userId || !currentChatSubject) return null;
    
    try {
      const exam = await apiService.createExam(
        userId,
        `${currentChatSubject} Exam`,
        currentChatSubject,
        currentChatId
      );
      setCurrentExamId(exam.exam_id);
      return exam;
    } catch (error) {
      console.error('Failed to create exam:', error);
      return null;
    }
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
      <div className="w-64 bg-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-300">
          <h2 className="text-lg font-semibold text-gray-800">Chat History</h2>
        </div>
        
        {/* New Chat Button */}
        <div className="p-4 space-y-2">
          <button 
            onClick={handleNewChat}
            className="w-full bg-black text-white py-2 px-4 rounded-lg font-medium hover:bg-gray-800 transition-colors flex items-center justify-center gap-2"
          >
            <span className="text-lg">+</span>
            New Chat
          </button>
          
          <button
            onClick={() => {
              console.log('Manual chat refresh clicked');
              loadUserChats();
            }}
            className="w-full bg-gray-100 text-gray-700 py-1 px-2 rounded text-xs hover:bg-gray-200 h-10"
          >
            🔄 Refresh Chats
          </button>
        </div>
        
        {/* Chat List */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-2">
            {userChats.length > 0 ? (
              <div className="space-y-1">
                {console.log('Rendering chat list. UserChats:', userChats)}
                {userChats.map((chat) => (
                  <button
                    key={chat.chat_id}
                    onClick={() => {
                      console.log('Clicking on chat:', chat.chat_id, chat.subject);
                      loadChat(chat);
                    }}
                    className={`w-full text-left p-3 rounded-lg transition-colors hover:bg-gray-300 ${
                      currentChatId === chat.chat_id ? 'bg-gray-300' : ''
                    }`}
                  >
                    <div className="font-medium text-gray-800 truncate">
                      {chat.subject || 'Untitled Chat'}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {new Date(chat.updated_at || chat.created_at).toLocaleDateString()}
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="p-4 text-center text-gray-600">
                <p>No chats yet.</p>
                <p className="text-sm mt-1">Start a new conversation!</p>
              </div>
            )}
          </div>
        </div>
        
        {/* Bottom Icons */}
        <div className="p-4 border-t border-gray-300 space-y-4 flex flex-row space-between w-full justify-between">
          {/* Settings Icon */}
          <button className="p-2 hover:bg-gray-300 rounded-lg transition-colors">
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
          
          {/* User Avatar */}
          <div className="w-8 h-8 bg-orange-400 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-medium">
              {user?.user_metadata?.display_name?.[0] || user?.email?.[0] || 'U'}
            </span>
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
            <div>
              <h2 className="text-lg font-medium text-gray-900">AI Assistant</h2>
              {currentChatSubject && (
                <p className="text-sm text-gray-500">{currentChatSubject}</p>
              )}
            </div>
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
                <p className="text-sm leading-relaxed">{cleanResponse(text)}</p>
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
          {/* Exam Mode Toggle */}
          <div className="mb-4 flex items-center justify-between">
            <span className="text-sm text-gray-600">
              {isExamMode ? 'Exam Mode' : 'Chat Mode'}
            </span>
            <button
              onClick={toggleExamMode}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 ${
                isExamMode ? 'bg-black' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  isExamMode ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {!isExamMode ? (
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
          ) : (
            <div className="text-center text-gray-600">
              <p className="text-sm">Exam mode is active. Use the exam panel to create and take exams.</p>
            </div>
          )}
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
        {!isExamMode ? (
          /* Chat Mode - Show exam info, score summary, or history */
          <div className="p-6 flex flex-col h-full">
            {currentExam && examResults ? (
              /* Show Exam Score Summary */
              <div className="flex-1 flex flex-col">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Exam Results</h3>
                  <button
                    onClick={() => {
                      setCurrentExam(null);
                      setExamResults(null);
                      setExamAnswers([]);
                    }}
                    className="text-gray-500 hover:text-gray-700 transition-colors"
                  >
                    ✕ Close
                  </button>
                </div>
                
                <div className="bg-white rounded-lg p-6 border shadow-sm mb-4">
                  <h4 className="text-xl font-bold text-gray-900 mb-2">{currentExam.title}</h4>
                  <p className="text-gray-600 mb-4">{currentExam.subject}</p>
                  
                  <div className="text-center mb-6">
                    <div className="bg-gray-100 rounded-lg p-6">
                      <div className="text-4xl font-bold text-gray-900 mb-2">
                        {examResults.score}/{examResults.max_score}
                      </div>
                      <div className="text-2xl font-semibold text-gray-700 mb-1">
                        {examResults.percentage.toFixed(1)}%
                      </div>
                      <div className={`text-sm font-medium ${
                        examResults.percentage >= 80 ? 'text-green-600' :
                        examResults.percentage >= 60 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {examResults.percentage >= 80 ? 'Excellent!' :
                         examResults.percentage >= 60 ? 'Good Job!' : 'Keep Practicing!'}
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Exam Type:</span>
                      <span className="font-medium">{currentExam.exam_type ? currentExam.exam_type.toUpperCase() : 'MCQ'}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Questions:</span>
                      <span className="font-medium">{currentExam.questions?.length || 0}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Date Completed:</span>
                      <span className="font-medium">{new Date(currentExam.updated_at || currentExam.created_at).toLocaleDateString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Status:</span>
                      <span className="font-medium text-green-600">Completed</span>
                    </div>
                  </div>
                </div>
                
                <button
                  onClick={() => {
                    setShowExamHistory(true);
                    setCurrentExam(null);
                    setExamResults(null);
                    setExamAnswers([]);
                  }}
                  className="bg-gray-100 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-200 transition-colors"
                >
                  ← Back to Exam History
                </button>
              </div>
            ) : (
              /* Show Exam History or Controls */
              <>
                <div className="flex flex-col gap-2 mb-4">
                  <button
                    onClick={() => {
                      console.log('Toggling exam history. Current state:', showExamHistory);
                      console.log('Current userExams:', userExams);
                      console.log('UserId:', userId);
                      setShowExamHistory(!showExamHistory);
                    }}
                    className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-200 transition-colors"
                  >
                    {showExamHistory ? 'Hide' : 'View'} Exam History ({userExams.length})
                  </button>
                  
                  <button
                    onClick={() => {
                      console.log('Manual exam refresh clicked');
                      loadUserExams();
                    }}
                    className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-200 transition-colors text-sm"
                  >
                    🔄 Refresh Exams
                  </button>
                </div>
                  
                  {showExamHistory && (
                    <div className="flex-1 flex flex-col min-h-0">
                      <h4 className="font-medium text-gray-900 text-base mb-3">Previous Exams:</h4>
                      {console.log('Rendering exam history. ShowExamHistory:', showExamHistory, 'UserExams:', userExams)}
                      <div className="flex-1 overflow-y-auto space-y-3">
                        {userExams.length === 0 ? (
                          <div className="text-center py-12 text-gray-500">
                            <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                            </svg>
                            <p className="text-lg font-medium text-gray-900 mb-1">No exams yet</p>
                            <p className="text-sm">Create your first exam to see it here</p>
                          </div>
                        ) : (
                          userExams.map((exam) => (
                          <div
                            key={exam.exam_id}
                            onClick={() => {
                              console.log('Clicking on exam:', exam.exam_id);
                              loadExamFromHistory(exam.exam_id);
                            }}
                            className="bg-white p-4 rounded-lg border cursor-pointer hover:shadow-md transition-all"
                          >
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <h5 className="text-base font-medium text-gray-900 mb-1">
                                  {exam.title}
                                </h5>
                                <p className="text-sm text-gray-600 mb-2">{exam.subject}</p>
                                <div className="flex items-center gap-3">
                                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                                    exam.status === 'completed' 
                                      ? 'bg-green-100 text-green-800' 
                                      : 'bg-yellow-100 text-yellow-800'
                                  }`}>
                                    {exam.status}
                                  </span>
                                  <span className="text-xs text-gray-500">
                                    {exam.exam_type ? exam.exam_type.toUpperCase() : 'MCQ'}
                                  </span>
                                  <span className="text-xs text-gray-500">
                                    {new Date(exam.updated_at || exam.created_at).toLocaleDateString()}
                                  </span>
                                </div>
                              </div>
                              {exam.status === 'completed' && typeof exam.percentage === 'number' && !isNaN(exam.percentage) && (
                                <div className="text-right">
                                  <div className="text-lg font-bold text-gray-900">
                                    {exam.percentage.toFixed(0)}%
                                  </div>
                                  <div className="text-xs text-gray-500">
                                    {exam.score || 0}/{exam.max_score || 0}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        ) : (
          <>
            {/* Exam Header */}
            <div className="px-6 py-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">
                  {currentExam ? currentExam.title : 'Exam Center'}
                </h2>
                <button 
                  onClick={toggleExamMode}
                  className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
                  title="Exit Exam Mode"
                >
                  <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Exam Content */}
            <div className="flex-1 overflow-y-auto">
              {showExamForm ? (
                /* Exam Creation Form */
                <div className="p-6 space-y-6">
                  <h3 className="text-lg font-semibold text-gray-900">Create New Exam</h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Exam Title *
                      </label>
                      <input
                        type="text"
                        value={examForm.title}
                        onChange={(e) => handleExamFormChange('title', e.target.value)}
                        placeholder="e.g., Math Quiz 1"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Subject *
                      </label>
                      <input
                        type="text"
                        value={examForm.subject}
                        onChange={(e) => handleExamFormChange('subject', e.target.value)}
                        placeholder="e.g., Mathematics"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Exam Type
                      </label>
                      <select
                        value={examForm.exam_type}
                        onChange={(e) => handleExamFormChange('exam_type', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                      >
                        <option value="mcq">Multiple Choice (MCQ)</option>
                        <option value="written">Written/Essay</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Number of Questions
                      </label>
                      <select
                        value={examForm.num_questions}
                        onChange={(e) => handleExamFormChange('num_questions', parseInt(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                      >
                        <option value={5}>5 Questions</option>
                        <option value={10}>10 Questions</option>
                        <option value={15}>15 Questions</option>
                        <option value={20}>20 Questions</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Difficulty Level
                      </label>
                      <select
                        value={examForm.difficulty}
                        onChange={(e) => handleExamFormChange('difficulty', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                      >
                        <option value="easy">Easy</option>
                        <option value="medium">Medium</option>
                        <option value="hard">Hard</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Specific Topic (Optional)
                      </label>
                      <input
                        type="text"
                        value={examForm.topic}
                        onChange={(e) => handleExamFormChange('topic', e.target.value)}
                        placeholder="e.g., Algebra, Calculus"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                      />
                    </div>
                  </div>

                  <button
                    onClick={generateExam}
                    disabled={isLoading || !examForm.title.trim() || !examForm.subject.trim()}
                    className="w-full bg-black text-white py-3 px-4 rounded-lg font-medium hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mb-3"
                  >
                    {isLoading ? 'Generating...' : 'Generate Exam'}
                  </button>
                  
                </div>
              ) : currentExam && !examResults ? (
                /* Exam Taking Interface */
                <div className="flex flex-col h-full">
                  {/* Question Progress */}
                  <div className="px-6 py-4 border-b border-gray-200 bg-white">
                    <div className="flex justify-between items-center text-sm text-gray-600">
                      <span>Question {currentQuestionIndex + 1} of {currentExam.questions.length}</span>
                      <span>{currentExam.exam_type ? currentExam.exam_type.toUpperCase() : 'MCQ'} Exam</span>
                    </div>
                    <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-black h-2 rounded-full transition-all"
                        style={{ width: `${((currentQuestionIndex + 1) / currentExam.questions.length) * 100}%` }}
                      />
                    </div>
                  </div>

                  {/* Question Content */}
                  <div className="flex-1 p-6 overflow-y-auto">
                    {currentExam.questions[currentQuestionIndex] && (
                      <div className="space-y-6">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 mb-4">
                            Question {currentQuestionIndex + 1}:
                          </h3>
                          <p className="text-gray-700 text-base mb-6">
                            {currentExam.questions[currentQuestionIndex].question}
                          </p>
                        </div>

                        {(currentExam.exam_type || 'mcq') === 'mcq' ? (
                          /* MCQ Options */
                          <div className="space-y-3">
                            {currentExam.questions[currentQuestionIndex].options?.map((option, index) => (
                              <label 
                                key={option.id || index} 
                                className="flex items-center space-x-3 cursor-pointer p-3 rounded-lg hover:bg-gray-100 transition-colors"
                              >
                                <input
                                  type="radio"
                                  name={`question-${currentExam.questions[currentQuestionIndex].id}`}
                                  value={option.id}
                                  checked={examAnswers.find(a => a.question_id === currentExam.questions[currentQuestionIndex].id)?.answer === option.id}
                                  onChange={() => handleAnswerSelect(currentExam.questions[currentQuestionIndex].id, option.id)}
                                  className="w-4 h-4 text-black border-2 border-gray-300 focus:ring-black"
                                />
                                <span className="text-gray-700 text-base">{option.text}</span>
                              </label>
                            ))}
                          </div>
                        ) : (
                          /* Written Answer */
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Your Answer:
                            </label>
                            <textarea
                              value={examAnswers.find(a => a.question_id === currentExam.questions[currentQuestionIndex].id)?.answer || ''}
                              onChange={(e) => handleAnswerSelect(currentExam.questions[currentQuestionIndex].id, e.target.value)}
                              placeholder="Write your answer here..."
                              rows={8}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm resize-none"
                            />
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Navigation Buttons */}
                  <div className="p-6 border-t border-gray-200 bg-white">
                    <div className="flex justify-between">
                      <button
                        onClick={previousQuestion}
                        disabled={currentQuestionIndex === 0}
                        className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        ← Previous
                      </button>
                      
                      {currentQuestionIndex < currentExam.questions.length - 1 ? (
                        <button
                          onClick={nextQuestion}
                          className="px-6 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors"
                        >
                          Next →
                        </button>
                      ) : (
                        <button
                          onClick={submitExam}
                          disabled={isLoading}
                          className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                        >
                          {isLoading ? 'Submitting...' : 'Submit Exam'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ) : examResults ? (
                /* Exam Results */
                <div className="p-6 space-y-6">
                  <div className="text-center">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Exam Completed!</h3>
                    <div className="bg-gray-100 rounded-lg p-4 mb-4">
                      <div className="text-3xl font-bold text-gray-900 mb-1">
                        {examResults.score}/{examResults.max_score}
                      </div>
                      <div className="text-lg text-gray-600">
                        {examResults.percentage.toFixed(1)}%
                      </div>
                    </div>
                  </div>

                  {examResults.results?.question_results && (
                    <div className="space-y-4">
                      <h4 className="font-medium text-gray-900">Question Results:</h4>
                      <div className="space-y-3 max-h-64 overflow-y-auto">
                        {examResults.results.question_results.map((result, index) => (
                          <div key={index} className="bg-white p-3 rounded-lg border">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm font-medium">Q{index + 1}</span>
                              {(currentExam.exam_type || 'mcq') === 'mcq' ? (
                                <span className={`text-sm ${result.is_correct ? 'text-green-600' : 'text-red-600'}`}>
                                  {result.is_correct ? '✓ Correct' : '✗ Wrong'}
                                </span>
                              ) : (
                                <span className="text-sm text-gray-600">
                                  {result.score}/{result.max_points}
                                </span>
                              )}
                            </div>
                            {result.feedback && (
                              <p className="text-xs text-gray-600">{result.feedback}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <button
                    onClick={restartExam}
                    className="w-full bg-black text-white py-3 px-4 rounded-lg font-medium hover:bg-gray-800 transition-colors"
                  >
                    Create New Exam
                  </button>
                </div>
              ) : null}
            </div>
          </>
        )}
      </div>

      {/* New Chat Modal */}
      {showNewChatModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="mb-4">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Start New Chat</h3>
              <p className="text-sm text-gray-600">What subject would you like to discuss?</p>
            </div>
            
            <div className="mb-6">
              <input
                type="text"
                value={newChatSubject}
                onChange={(e) => setNewChatSubject(e.target.value)}
                placeholder="e.g., Mathematics, Physics, Programming..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    createNewChat();
                  } else if (e.key === 'Escape') {
                    cancelNewChat();
                  }
                }}
              />
            </div>
            
            <div className="flex gap-3 justify-end">
              <button
                onClick={cancelNewChat}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={createNewChat}
                disabled={!newChatSubject.trim()}
                className="px-6 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Start Chat
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatPage;