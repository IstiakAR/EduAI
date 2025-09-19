import { useState, useEffect } from "react";
import { useAuth } from '../hooks/useAuth';
import Layout from './Layout';
import Avatar from './Avatar';
import supabase from '../supabase';
import { useNavigate } from 'react-router-dom';

function Dashboard({ onNavigate }) {
    const { user, loading } = useAuth();
    const navigate = useNavigate();
    const [stats, setStats] = useState({
        questionsAsked: 0,
        examsCompleted: 0,
        hoursStudied: 0,
        currentStreak: 0
    });
    const [recentActivity, setRecentActivity] = useState([]);
    const [dataLoading, setDataLoading] = useState(true);

    // Add timeout to prevent infinite loading
    useEffect(() => {
        const timeout = setTimeout(() => {
            console.log('Dashboard loading timeout - forcing load completion');
            setDataLoading(false);
        }, 10000); // 10 second timeout

        return () => clearTimeout(timeout);
    }, []);

    // Fetch user statistics and recent activity
    useEffect(() => {
        console.log('Dashboard useEffect triggered, user:', user?.id);
        if (user?.id) {
            fetchUserStats();
            fetchRecentActivity();
        } else {
            // If no user, stop loading
            setDataLoading(false);
        }
    }, [user?.id]);

    const fetchUserStats = async () => {
        try {
            console.log('Fetching user stats for user:', user.id);
            
            // Get total chats (questions asked)
            const { data: chats, error: chatsError } = await supabase
                .from('chats')
                .select('chat_id, chat_data, created_at')
                .eq('user_id', user.id);

            console.log('Chats result:', { chats, chatsError });

            if (chatsError) {
                console.error('Chats error:', chatsError);
                // Don't throw, continue with other queries
            }

            // Get completed exams
            const { data: exams, error: examsError } = await supabase
                .from('exams')
                .select('exam_id, status, created_at')
                .eq('user_id', user.id);

            console.log('Exams result:', { exams, examsError });

            if (examsError) {
                console.error('Exams error:', examsError);
                // Don't throw, continue with calculation
            }

            // Calculate questions asked (count messages in all chats)
            let totalQuestions = 0;
            if (chats && !chatsError) {
                chats.forEach(chat => {
                    const messages = chat.chat_data?.messages || [];
                    // Count user messages only
                    totalQuestions += messages.filter(msg => msg.role === 'user').length;
                });
            }
            totalQuestions = chats.length;

            // Calculate completed exams
            const completedExams = (exams && !examsError) ? exams.filter(exam => exam.status === 'completed').length : 0;

            // Calculate hours studied (rough estimate: 10 minutes per question + 30 minutes per exam)
            const hoursStudied = Math.round((totalQuestions * 10 + completedExams * 30) / 60);

            // Calculate current streak (simplified - count consecutive days with activity)
            const currentStreak = calculateStreak(chats, exams);

            const newStats = {
                questionsAsked: totalQuestions,
                examsCompleted: completedExams,
                hoursStudied: hoursStudied,
                currentStreak: currentStreak
            };

            console.log('Calculated stats:', newStats);
            setStats(newStats);

        } catch (error) {
            console.error('Error fetching user stats:', error);
            // Keep default values on error
        } finally {
            console.log('Setting dataLoading to false for stats');
            setDataLoading(false);
        }
    };

    const fetchRecentActivity = async () => {
        try {
            console.log('Fetching recent activity for user:', user.id);
            
            // Get recent chats
            const { data: recentChats, error: chatsError } = await supabase
                .from('chats')
                .select('chat_id, title, subject, chat_data, created_at, updated_at')
                .eq('user_id', user.id)
                .order('updated_at', { ascending: false })
                .limit(3);

            console.log('Recent chats result:', { recentChats, chatsError });

            if (chatsError) {
                console.error('Recent chats error:', chatsError);
            }

            // Get recent exams
            const { data: recentExams, error: examsError } = await supabase
                .from('exams')
                .select('exam_id, title, subject, exam_data, status, created_at, updated_at')
                .eq('user_id', user.id)
                .order('updated_at', { ascending: false })
                .limit(3);

            console.log('Recent exams result:', { recentExams, examsError });

            if (examsError) {
                console.error('Recent exams error:', examsError);
            }

            // Combine and format activity
            const activity = [];

            // Add recent chats
            if (recentChats && !chatsError) {
                recentChats.forEach(chat => {
                    const messages = chat.chat_data?.messages || [];
                    const lastUserMessage = messages.filter(msg => msg.role === 'user').pop();
                    if (lastUserMessage) {
                        activity.push({
                            id: `chat-${chat.chat_id}`,
                            type: 'question',
                            title: lastUserMessage.content.substring(0, 50) + (lastUserMessage.content.length > 50 ? '...' : ''),
                            time: formatTimeAgo(chat.updated_at),
                            timestamp: new Date(chat.updated_at)
                        });
                    }
                });
            }

            // Add recent exams
            if (recentExams && !examsError) {
                recentExams.forEach(exam => {
                    const score = exam.exam_data?.results?.score_percentage;
                    activity.push({
                        id: `exam-${exam.exam_id}`,
                        type: 'exam',
                        title: exam.title,
                        score: score ? `${Math.round(score)}%` : exam.status === 'completed' ? 'Completed' : 'In Progress',
                        time: formatTimeAgo(exam.updated_at),
                        timestamp: new Date(exam.updated_at)
                    });
                });
            }

            // Sort by timestamp and take top 4
            activity.sort((a, b) => b.timestamp - a.timestamp);
            console.log('Final activity:', activity);
            setRecentActivity(activity.slice(0, 4));

        } catch (error) {
            console.error('Error fetching recent activity:', error);
            setRecentActivity([]);
        }
    };

    const calculateStreak = (chats, exams) => {
        // Simple streak calculation - count consecutive days with activity
        const activities = [];
        
        if (chats) {
            chats.forEach(chat => activities.push(new Date(chat.created_at)));
        }
        if (exams) {
            exams.forEach(exam => activities.push(new Date(exam.created_at)));
        }

        if (activities.length === 0) return 0;

        // Sort dates
        activities.sort((a, b) => b - a);
        
        // Get unique days
        const uniqueDays = [...new Set(activities.map(date => date.toDateString()))];
        
        // Calculate streak from today backwards
        const today = new Date();
        let streak = 0;
        
        for (let i = 0; i < uniqueDays.length; i++) {
            const daysDiff = Math.floor((today - new Date(uniqueDays[i])) / (1000 * 60 * 60 * 24));
            if (daysDiff === streak) {
                streak++;
            } else {
                break;
            }
        }
        
        return streak;
    };

    const formatTimeAgo = (dateString) => {
        const now = new Date();
        const date = new Date(dateString);
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
        if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;
        return `${Math.floor(diffInSeconds / 604800)} weeks ago`;
    };

    const [quickActions] = useState([
        { id: 1, title: 'Ask a Question', description: 'Get instant AI-powered answers', action: 'chat' },
        { id: 2, title: 'Take an Exam', description: 'Test your knowledge', action: 'chat' },
    ]);

    if (loading || dataLoading) {
        return (
            <Layout>
                <div className="flex items-center justify-center min-h-[60vh]">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
                        <div className="text-lg">Loading your dashboard...</div>
                    </div>
                </div>
            </Layout>
        );
    }

    if (!user) {
        return (
            <Layout>
                <div className="flex items-center justify-center min-h-[60vh]">
                    <div className="text-center">
                        <h2 className="text-2xl font-bold mb-4">Please sign in to access your dashboard</h2>
                        <a 
                            href="/" 
                            className="px-6 py-3 bg-black text-white rounded hover:bg-gray-800 transition-colors"
                        >
                            Go to Home
                        </a>
                    </div>
                </div>
            </Layout>
        );
    }

    return (
        <Layout onNavigate={onNavigate}>
            {/* Dashboard Header */}
            <section className="px-6 py-8 md:px-12 md:py-12">
                <div className="max-w-6xl mx-auto">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
                        <div className="mb-6 md:mb-0">
                            <div className="w-16 h-1 bg-black mb-4"></div>
                            <h1 className="text-3xl md:text-4xl font-bold mb-2">
                                Welcome back, {user.user_metadata?.full_name || user.email?.split('@')[0] || 'User'}!
                            </h1>
                            <p className="text-lg text-gray-600">Ready to continue your learning journey?</p>
                        </div>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 mb-12">
                        <div className="bg-gray-50 p-6 rounded-sm border border-gray-200">
                            <div className="text-2xl md:text-3xl font-bold mb-2">{stats.questionsAsked}</div>
                            <div className="text-sm text-gray-600">Questions Asked</div>
                        </div>
                        <div className="bg-gray-50 p-6 rounded-sm border border-gray-200">
                            <div className="text-2xl md:text-3xl font-bold mb-2">{stats.examsCompleted}</div>
                            <div className="text-sm text-gray-600">Exams Completed</div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Quick Actions */}
            <section className="px-6 py-8 md:px-12">
                <div className="max-w-6xl mx-auto">
                    <div className="mb-8">
                        <div className="w-16 h-1 bg-black mb-4"></div>
                        <h2 className="text-2xl md:text-3xl font-bold">Quick Actions</h2>
                    </div>
                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {quickActions.map((action) => (
                            <button
                                key={action.id}
                                onClick={() => navigate('/' + action.action)}
                                className="p-6 border border-black rounded-sm hover:bg-gray-50 transition-colors text-left group"
                            >
                                <div className="text-3xl mb-4">{action.icon}</div>
                                <h3 className="text-lg font-bold mb-2 group-hover:underline">{action.title}</h3>
                                <p className="text-sm text-gray-600">{action.description}</p>
                            </button>
                        ))}
                    </div>
                </div>
            </section>

            {/* Recent Activity */}
            <section className="px-6 py-8 md:px-12">
                <div className="max-w-6xl mx-auto">
                    <div className="mb-8">
                        <div className="w-16 h-1 bg-black mb-4"></div>
                        <h2 className="text-2xl md:text-3xl font-bold">Recent Activity</h2>
                    </div>
                    <div className="space-y-4">
                        {recentActivity.length > 0 ? (
                            recentActivity.map((activity) => (
                                <div key={activity.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-sm hover:bg-gray-50 transition-colors">
                                    <div className="flex items-center space-x-4">
                                        <div className="w-2 h-2 bg-black rounded-full"></div>
                                        <div>
                                            <h3 className="font-medium">{activity.title}</h3>
                                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                                                <span className="capitalize">{activity.type}</span>
                                                {activity.score && (
                                                    <>
                                                        <span>•</span>
                                                        <span className="font-medium text-green-600">{activity.score}</span>
                                                    </>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="text-sm text-gray-500">{activity.time}</div>
                                </div>
                            ))
                        ) : (
                            <div className="text-center py-8 text-gray-500">
                                <p>No recent activity yet.</p>
                                <p className="text-sm mt-2">Start by asking a question or taking an exam!</p>
                            </div>
                        )}
                    </div>
                </div>
            </section>
        </Layout>
    );
}

export default Dashboard;