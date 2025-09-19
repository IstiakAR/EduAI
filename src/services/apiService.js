// Simple API service for backend communication
import supabase from '../supabase';

class ApiService {
  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8001';
  }

  async sendMessage(message, context = null) {
    try {
      const response = await fetch(`${this.baseURL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('API Error:', error);
      throw new Error(`Failed to get AI response: ${error.message}`);
    }
  }

  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      return response.ok;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }

  // Exam operations using Supabase + AI generation
  async generateExam(examData) {
    try {
      console.log('Generating exam with AI:', examData);
      
      // First, generate exam content using AI
      const aiPrompt = this.createExamPrompt(examData);
      const aiResponse = await this.sendMessage(aiPrompt);
      
      // Parse AI response to extract questions
      const examQuestions = this.parseAIExamResponse(aiResponse, examData.exam_type);
      
      // Calculate max score
      const maxScore = examData.exam_type === 'mcq' 
        ? examQuestions.length 
        : examQuestions.reduce((sum, q) => sum + (q.max_points || 10), 0);
      
      // Create exam record in Supabase
      const { data, error } = await supabase
        .from('exams')
        .insert({
          user_id: examData.user_id,
          chat_id: examData.chat_id,
          title: examData.title,
          subject: examData.subject,
          exam_data: {
            questions: examQuestions,
            user_answers: [],
            results: {},
            exam_type: examData.exam_type,
            difficulty: examData.difficulty,
            max_score: maxScore
          },
          status: 'in_progress'
        })
        .select()
        .single();

      if (error) throw error;
      
      return {
        exam_id: data.exam_id,
        title: data.title,
        subject: data.subject,
        exam_type: examData.exam_type,
        questions: examQuestions,
        total_questions: examQuestions.length,
        max_score: maxScore,
        success: true
      };
    } catch (error) {
      console.error('Error generating exam:', error);
      throw error;
    }
  }

  createExamPrompt(examData) {
    if (examData.exam_type === 'mcq') {
      return `Generate ${examData.num_questions} multiple choice questions for ${examData.subject}.
Title: ${examData.title}
Difficulty: ${examData.difficulty}
${examData.topic ? `Topic: ${examData.topic}` : ''}

For each question, provide:
1. The question text
2. 4 answer options (A, B, C, D)
3. The correct answer
4. A brief explanation

Format the response as a JSON array:
[
  {
    "id": "q1",
    "question": "Question text here?",
    "options": [
      {"id": "A", "text": "Option A text", "is_correct": false},
      {"id": "B", "text": "Option B text", "is_correct": true},
      {"id": "C", "text": "Option C text", "is_correct": false},
      {"id": "D", "text": "Option D text", "is_correct": false}
    ],
    "correct_answer": "B",
    "explanation": "Explanation here"
  }
]`;
    } else {
      return `Generate ${examData.num_questions} written/essay questions for ${examData.subject}.
Title: ${examData.title}
Difficulty: ${examData.difficulty}
${examData.topic ? `Topic: ${examData.topic}` : ''}

For each question, provide:
1. The question text
2. Maximum points (distribute 100 points total across all questions)
3. A sample answer or key points

Format the response as a JSON array:
[
  {
    "id": "q1",
    "question": "Question text here?",
    "max_points": 20,
    "sample_answer": "Sample answer or key points here"
  }
]`;
    }
  }

  parseAIExamResponse(aiResponse, examType) {
    try {
      // Extract JSON from AI response
      const start_idx = aiResponse.indexOf('[');
      const end_idx = aiResponse.lastIndexOf(']') + 1;
      
      if (start_idx === -1 || end_idx === 0) {
        throw new Error('No JSON array found in AI response');
      }
      
      const jsonStr = aiResponse.substring(start_idx, end_idx);
      const questions = JSON.parse(jsonStr);
      
      return questions;
    } catch (error) {
      console.error('Failed to parse AI response, using fallback questions:', error);
      
      // Fallback questions
      if (examType === 'mcq') {
        return [
          {
            id: "q1",
            question: `Sample ${examType} question about the subject?`,
            options: [
              { id: "A", text: "Option A", is_correct: true },
              { id: "B", text: "Option B", is_correct: false },
              { id: "C", text: "Option C", is_correct: false },
              { id: "D", text: "Option D", is_correct: false }
            ],
            correct_answer: "A",
            explanation: "This is a sample explanation."
          }
        ];
      } else {
        return [
          {
            id: "q1",
            question: "Sample written question about the subject?",
            max_points: 100,
            sample_answer: "This is a sample answer."
          }
        ];
      }
    }
  }

  async getUserExams(userId) {
    try {
      console.log('=== API SERVICE: Getting user exams ===');
      console.log('UserId parameter:', userId);
      console.log('UserId type:', typeof userId);
      console.log('Supabase client available:', !!supabase);
      
      const { data, error } = await supabase
        .from('exams')
        .select(`
          exam_id,
          title,
          subject,
          status,
          created_at,
          updated_at,
          exam_data
        `)
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

      console.log('Supabase query result:');
      console.log('- Data:', data);
      console.log('- Error:', error);
      console.log('- Data length:', data?.length);

      if (error) {
        console.error('Supabase error details:', error);
        throw error;
      }
      
      // Transform data for frontend
      const transformedData = data.map(exam => ({
        exam_id: exam.exam_id,
        title: exam.title,
        subject: exam.subject,
        exam_type: exam.exam_data?.exam_type || 'mcq',
        status: exam.status,
        created_at: exam.created_at,
        updated_at: exam.updated_at,
        total_questions: exam.exam_data?.questions?.length || 0,
        max_score: exam.exam_data?.max_score || 0,
        score: exam.exam_data?.results?.score || null,
        percentage: exam.exam_data?.results?.percentage || null
      }));
      
      console.log('Transformed data:', transformedData);
      console.log('=== API SERVICE: getUserExams complete ===');
      return transformedData;
    } catch (error) {
      console.error('Error getting user exams:', error);
      throw error;
    }
  }

  async getExamById(examId) {
    try {
      console.log('=== API SERVICE: Getting exam by ID ===');
      console.log('Exam ID:', examId);
      
      const { data, error } = await supabase
        .from('exams')
        .select('*')
        .eq('exam_id', examId)
        .single();

      console.log('Supabase response:');
      console.log('- Data:', data);
      console.log('- Error:', error);

      if (error) {
        console.error('Supabase error:', error);
        throw error;
      }
      
      const result = {
        exam_id: data.exam_id,
        title: data.title,
        subject: data.subject,
        exam_type: data.exam_data?.exam_type || 'mcq',
        status: data.status,
        exam_data: data.exam_data, // This was missing!
        questions: data.exam_data?.questions || [],
        total_questions: data.exam_data?.questions?.length || 0,
        max_score: data.exam_data?.max_score || 0,
        created_at: data.created_at,
        updated_at: data.updated_at,
        success: true
      };
      
      console.log('Returning exam result:', result);
      console.log('=== API SERVICE: getExamById complete ===');
      return result;
    } catch (error) {
      console.error('Error getting exam:', error);
      throw error;
    }
  }

  async submitExam(examId, userId, answers) {
    try {
      console.log('Submitting exam to Supabase:', { examId, userId, answers });
      
      // First, get the current exam data
      const { data: examData, error: fetchError } = await supabase
        .from('exams')
        .select('*')
        .eq('exam_id', examId)
        .eq('user_id', userId)
        .single();

      if (fetchError) throw fetchError;
      
      const questions = examData.exam_data?.questions || [];
      const examType = examData.exam_data?.exam_type || 'mcq';
      
      // Grade the exam
      const results = await this.gradeExam(questions, answers, examType);
      
      // Update exam with results
      const { data, error } = await supabase
        .from('exams')
        .update({
          exam_data: {
            ...examData.exam_data,
            user_answers: answers,
            results: results
          },
          status: 'completed',
          updated_at: new Date().toISOString()
        })
        .eq('exam_id', examId)
        .eq('user_id', userId)
        .select()
        .single();

      if (error) throw error;
      
      return {
        exam_id: examId,
        score: results.score,
        max_score: results.max_score,
        percentage: results.percentage,
        results: results,
        success: true
      };
    } catch (error) {
      console.error('Error submitting exam:', error);
      throw error;
    }
  }

  async gradeExam(questions, answers, examType) {
    if (examType === 'mcq') {
      return this.gradeMCQExam(questions, answers);
    } else {
      return this.gradeWrittenExam(questions, answers);
    }
  }

  gradeMCQExam(questions, answers) {
    let score = 0;
    const questionResults = [];
    
    // Create answer lookup
    const answerMap = {};
    answers.forEach(ans => {
      answerMap[ans.question_id] = ans.answer;
    });
    
    questions.forEach(question => {
      const userAnswer = answerMap[question.id] || '';
      const correctAnswer = question.correct_answer;
      const isCorrect = userAnswer.toUpperCase() === correctAnswer.toUpperCase();
      
      if (isCorrect) score += 1;
      
      questionResults.push({
        question_id: question.id,
        question: question.question,
        user_answer: userAnswer,
        correct_answer: correctAnswer,
        is_correct: isCorrect,
        explanation: question.explanation || ''
      });
    });
    
    const maxScore = questions.length;
    const percentage = maxScore > 0 ? (score / maxScore) * 100 : 0;
    
    return {
      score,
      max_score: maxScore,
      percentage: Math.round(percentage * 100) / 100,
      question_results: questionResults,
      exam_type: 'mcq'
    };
  }

  async gradeWrittenExam(questions, answers) {
    let totalScore = 0;
    const questionResults = [];
    
    // Create answer lookup
    const answerMap = {};
    answers.forEach(ans => {
      answerMap[ans.question_id] = ans.answer;
    });
    
    for (const question of questions) {
      const userAnswer = answerMap[question.id] || '';
      const maxPoints = question.max_points || 10;
      
      if (!userAnswer.trim()) {
        questionResults.push({
          question_id: question.id,
          question: question.question,
          user_answer: userAnswer,
          score: 0,
          max_points: maxPoints,
          feedback: 'No answer provided.',
          strengths: '',
          improvements: 'Please provide an answer.'
        });
        continue;
      }
      
      // Use AI to grade written answers
      const gradingPrompt = `Grade this written answer on a scale of 0 to ${maxPoints}.

Question: ${question.question}

Student Answer: ${userAnswer}

Sample Answer/Key Points: ${question.sample_answer || 'No sample answer provided'}

Please provide a score from 0 to ${maxPoints} and brief feedback. Consider:
1. Accuracy and correctness
2. Completeness of answer
3. Understanding demonstrated
4. Clarity of explanation

Respond with just a number between 0 and ${maxPoints}.`;

      try {
        const gradeResponse = await this.sendMessage(gradingPrompt);
        
        // Extract numeric score from AI response
        const scoreMatch = gradeResponse.match(/(\d+(?:\.\d+)?)/);
        const questionScore = scoreMatch ? 
          Math.min(Math.max(parseFloat(scoreMatch[1]), 0), maxPoints) : 
          maxPoints * 0.5; // Default to 50% if parsing fails
        
        totalScore += questionScore;
        
        questionResults.push({
          question_id: question.id,
          question: question.question,
          user_answer: userAnswer,
          score: Math.round(questionScore * 100) / 100,
          max_points: maxPoints,
          feedback: 'Answer evaluated by AI grading system.',
          strengths: 'Response provided',
          improvements: questionScore < maxPoints * 0.8 ? 'Consider providing more detail or accuracy.' : 'Good work!'
        });
        
      } catch (error) {
        console.error('AI grading failed, using fallback:', error);
        // Fallback scoring based on length and effort
        const answerLength = userAnswer.trim().length;
        let questionScore;
        if (answerLength >= 100) questionScore = maxPoints * 0.8;
        else if (answerLength >= 50) questionScore = maxPoints * 0.6;
        else if (answerLength >= 20) questionScore = maxPoints * 0.4;
        else questionScore = maxPoints * 0.2;
        
        totalScore += questionScore;
        
        questionResults.push({
          question_id: question.id,
          question: question.question,
          user_answer: userAnswer,
          score: Math.round(questionScore * 100) / 100,
          max_points: maxPoints,
          feedback: 'Graded based on answer length and effort.',
          strengths: 'Answer provided',
          improvements: 'Consider providing more comprehensive responses.'
        });
      }
    }
    
    const maxScore = questions.reduce((sum, q) => sum + (q.max_points || 10), 0);
    const percentage = maxScore > 0 ? (totalScore / maxScore) * 100 : 0;
    
    return {
      score: Math.round(totalScore * 100) / 100,
      max_score: maxScore,
      percentage: Math.round(percentage * 100) / 100,
      question_results: questionResults,
      exam_type: 'written'
    };
  }

  // Chat storage methods
  async createChat(userId, title, subject = null) {
    try {
      console.log('apiService.createChat called with:', { userId, title, subject });
      const { data, error } = await supabase
        .from('chats')
        .insert({
          user_id: userId,
          title: title,
          subject: subject,
          chat_data: { messages: [], metadata: {} }
        })
        .select()
        .single();

      if (error) {
        console.error('Supabase error in createChat:', error);
        throw error;
      }
      console.log('Chat created successfully:', data);
      return data;
    } catch (error) {
      console.error('Error creating chat:', error);
      throw error;
    }
  }

  async updateChat(chatId, userId, messages, metadata = {}) {
    try {
      const { data, error } = await supabase
        .from('chats')
        .update({
          chat_data: { messages, metadata },
          updated_at: new Date().toISOString()
        })
        .eq('chat_id', chatId)
        .eq('user_id', userId)
        .select()
        .single();

      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Error updating chat:', error);
      throw error;
    }
  }

  async getUserChats(userId) {
    try {
      console.log('apiService.getUserChats called with userId:', userId);
      const { data, error } = await supabase
        .from('chats')
        .select('*')
        .eq('user_id', userId)
        .order('updated_at', { ascending: false });

      if (error) {
        console.error('Supabase error in getUserChats:', error);
        throw error;
      }
      console.log('Retrieved chats:', data);
      return data || [];
    } catch (error) {
      console.error('Error fetching user chats:', error);
      throw error;
    }
  }

  async getChat(chatId, userId) {
    try {
      const { data, error } = await supabase
        .from('chats')
        .select('*')
        .eq('chat_id', chatId)
        .eq('user_id', userId)
        .single();

      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Error fetching chat:', error);
      throw error;
    }
  }

  async deleteChat(chatId, userId) {
    try {
      const { error } = await supabase
        .from('chats')
        .delete()
        .eq('chat_id', chatId)
        .eq('user_id', userId);

      if (error) throw error;
      return true;
    } catch (error) {
      console.error('Error deleting chat:', error);
      throw error;
    }
  }

  // Exam storage methods
  async createExam(userId, title, subject, chatId = null) {
    try {
      const { data, error } = await supabase
        .from('exams')
        .insert({
          user_id: userId,
          chat_id: chatId,
          title: title,
          subject: subject,
          exam_data: { results: {}, questions: [], user_answers: [] },
          status: 'in_progress'
        })
        .select()
        .single();

      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Error creating exam:', error);
      throw error;
    }
  }

  async updateExam(examId, userId, examData, status = null) {
    try {
      const updateData = {
        exam_data: examData,
        updated_at: new Date().toISOString()
      };

      if (status) {
        updateData.status = status;
      }

      const { data, error } = await supabase
        .from('exams')
        .update(updateData)
        .eq('exam_id', examId)
        .eq('user_id', userId)
        .select()
        .single();

      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Error updating exam:', error);
      throw error;
    }
  }

  async getUserExams(userId) {
    try {
      const { data, error } = await supabase
        .from('exams')
        .select('*')
        .eq('user_id', userId)
        .order('updated_at', { ascending: false });

      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Error fetching user exams:', error);
      throw error;
    }
  }

  async getExam(examId, userId) {
    try {
      const { data, error } = await supabase
        .from('exams')
        .select('*')
        .eq('exam_id', examId)
        .eq('user_id', userId)
        .single();

      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Error fetching exam:', error);
      throw error;
    }
  }

  async deleteExam(examId, userId) {
    try {
      const { error } = await supabase
        .from('exams')
        .delete()
        .eq('exam_id', examId)
        .eq('user_id', userId);

      if (error) throw error;
      return true;
    } catch (error) {
      console.error('Error deleting exam:', error);
      throw error;
    }
  }

  async completeExam(examId, userId, finalAnswers, results) {
    try {
      const { data, error } = await supabase
        .from('exams')
        .update({
          exam_data: {
            questions: [], // Include questions if needed
            user_answers: finalAnswers,
            results: results
          },
          status: 'completed',
          updated_at: new Date().toISOString()
        })
        .eq('exam_id', examId)
        .eq('user_id', userId)
        .select()
        .single();

      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Error completing exam:', error);
      throw error;
    }
  }
}

export const apiService = new ApiService();