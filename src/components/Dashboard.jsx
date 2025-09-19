import { useState, useEffect } from "react";
import { useAuth } from '../hooks/useAuth';
import Layout from './Layout';
import Avatar from './Avatar';

function Dashboard() {
    const { user, loading } = useAuth();
    const [stats, setStats] = useState({
        questionsAsked: 42,
        examsCompleted: 8,
        hoursStudied: 24,
        currentStreak: 5
    });

    const [recentActivity] = useState([
        { id: 1, type: 'question', title: 'What is machine learning?', time: '2 hours ago' },
        { id: 2, type: 'exam', title: 'Python Fundamentals Quiz', score: '85%', time: '1 day ago' },
        { id: 3, type: 'question', title: 'Explain neural networks', time: '2 days ago' },
        { id: 4, type: 'exam', title: 'Data Structures Test', score: '92%', time: '3 days ago' },
    ]);

    const [quickActions] = useState([
        { id: 1, title: 'Ask a Question', description: 'Get instant AI-powered answers', icon: '❓', action: '/chat' },
        { id: 2, title: 'Take an Exam', description: 'Test your knowledge', icon: '📝', action: '/exam' },
        { id: 3, title: 'View Progress', description: 'Track your learning journey', icon: '📊', action: '/progress' },
        { id: 4, title: 'Study Materials', description: 'Access learning resources', icon: '📚', action: '/materials' },
    ]);

    if (loading) {
        return (
            <Layout>
                <div className="flex items-center justify-center min-h-[60vh]">
                    <div className="text-lg">Loading...</div>
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
        <Layout>
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
                        <div className="flex items-center space-x-4">
                            <Avatar 
                                src={user.user_metadata?.avatar_url}
                                alt={`${user.user_metadata?.full_name || user.email?.split('@')[0] || 'User'}'s avatar`}
                                size="w-16 h-16"
                                fallbackText={(user.user_metadata?.full_name || user.email?.split('@')[0] || 'U')[0].toUpperCase()}
                            />
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
                        <div className="bg-gray-50 p-6 rounded-sm border border-gray-200">
                            <div className="text-2xl md:text-3xl font-bold mb-2">{stats.hoursStudied}</div>
                            <div className="text-sm text-gray-600">Hours Studied</div>
                        </div>
                        <div className="bg-gray-50 p-6 rounded-sm border border-gray-200">
                            <div className="text-2xl md:text-3xl font-bold mb-2">{stats.currentStreak}</div>
                            <div className="text-sm text-gray-600">Day Streak</div>
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
                                onClick={() => window.location.href = action.action}
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
                        {recentActivity.map((activity) => (
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
                        ))}
                    </div>
                    <div className="text-center mt-8">
                        <button className="px-6 py-3 border border-black rounded hover:bg-gray-100 transition-colors">
                            View All Activity
                        </button>
                    </div>
                </div>
            </section>

            {/* Progress Section */}
            <section className="px-6 py-8 md:px-12">
                <div className="max-w-6xl mx-auto">
                    <div className="mb-8">
                        <div className="w-16 h-1 bg-black mb-4"></div>
                        <h2 className="text-2xl md:text-3xl font-bold">Learning Progress</h2>
                    </div>
                    <div className="grid md:grid-cols-2 gap-8">
                        <div className="bg-gray-50 p-8 rounded-sm border border-gray-200">
                            <h3 className="text-lg font-bold mb-4">Weekly Goal</h3>
                            <div className="mb-4">
                                <div className="flex justify-between text-sm mb-2">
                                    <span>5 of 7 days completed</span>
                                    <span>71%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                    <div className="bg-black h-2 rounded-full" style={{ width: '71%' }}></div>
                                </div>
                            </div>
                            <p className="text-sm text-gray-600">Keep it up! 2 more days to reach your weekly goal.</p>
                        </div>
                        <div className="bg-gray-50 p-8 rounded-sm border border-gray-200">
                            <h3 className="text-lg font-bold mb-4">Knowledge Areas</h3>
                            <div className="space-y-3">
                                <div className="flex justify-between items-center">
                                    <span className="text-sm">Machine Learning</span>
                                    <span className="text-sm font-medium">Advanced</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm">Python Programming</span>
                                    <span className="text-sm font-medium">Expert</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm">Data Structures</span>
                                    <span className="text-sm font-medium">Intermediate</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </Layout>
    );
}

export default Dashboard;