import { useState } from "react";
import { useAuth } from '../hooks/useAuth';
import Layout from './Layout';

function History() {
    const { user, loading } = useAuth();

    const [historyData] = useState({
        questions: [
            {
                id: 1,
                title: "What is machine learning and how does it differ from traditional programming?"
            },
            {
                id: 2,
                title: "Explain the concept of neural networks in deep learning"
            },
            {
                id: 3,
                title: "What are the key differences between supervised and unsupervised learning?"
            },
            {
                id: 4,
                title: "How do you implement a binary search algorithm in Python?"
            },
            {
                id: 5,
                title: "What is the time complexity of quicksort algorithm?"
            }
        ],
        exams: [
            {
                id: 1,
                title: "Python Fundamentals Quiz"
            },
            {
                id: 2,
                title: "Data Structures and Algorithms Test"
            },
            {
                id: 3,
                title: "Machine Learning Basics"
            },
            {
                id: 4,
                title: "JavaScript ES6 Features"
            }
        ]
    });

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
                        <h2 className="text-2xl font-bold mb-4">Please sign in to view your history</h2>
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
            <section className="px-6 py-8 md:px-12 md:py-12">
                <div className="max-w-4xl mx-auto">
                    {/* Questions */}
                    <div className="mb-12">
                        <div className="space-y-3">
                            {historyData.questions.map((question) => (
                                <div key={question.id} className="p-4 border border-gray-200 rounded-sm hover:bg-gray-50 transition-colors">
                                    <h3 className="text-gray-900">{question.title}</h3>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>
        </Layout>
    );
}

export default History;
