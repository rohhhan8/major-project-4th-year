// src/pages/QuizPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const QuizPage = () => {
    const { topic } = useParams();
    const navigate = useNavigate();
    const [quiz, setQuiz] = useState(null);
    const [answers, setAnswers] = useState([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchQuiz = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/quiz/${topic}`, {
                    withCredentials: true
                });
                setQuiz(response.data);
                // Initialize answers array
                setAnswers(new Array(response.data.questions.length).fill(null));
            } catch (err) {
                setError('Failed to load the quiz. Please try again.');
                console.error(err);
            }
        };
        fetchQuiz();
    }, [topic]);

    const handleOptionSelect = (optionIndex) => {
        const newAnswers = [...answers];
        newAnswers[currentQuestionIndex] = { question_index: currentQuestionIndex, option_index: optionIndex };
        setAnswers(newAnswers);
    };

    const handleNext = () => {
        if (currentQuestionIndex < quiz.questions.length - 1) {
            setCurrentQuestionIndex(currentQuestionIndex + 1);
        }
    };

    const handleSubmit = async () => {
        try {
            const submission = {
                topic: quiz.topic,
                answers: answers.filter(a => a !== null) // Filter out unanswered questions
            };
            const response = await axios.post('http://localhost:8000/quiz/submit', submission, {
                withCredentials: true
            });
            console.log('Quiz Results:', response.data);
            // We will build a results page later. For now, navigate back to topics.
            alert(`Quiz submitted! Your score: ${response.data.percentage}%`);
            navigate('/quiz/topics');
        } catch (err) {
            setError('Failed to submit the quiz.');
            console.error(err);
        }
    };

    if (error) return <div className="text-red-500 text-center p-8">{error}</div>;
    if (!quiz) return <div className="text-center p-8">Loading Quiz...</div>;

    const currentQuestion = quiz.questions[currentQuestionIndex];
    const selectedOption = answers[currentQuestionIndex]?.option_index;

    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
            <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-2xl">
                <h1 className="text-2xl font-bold mb-4">{quiz.topic}</h1>
                <div className="mb-6">
                    <p className="text-lg font-semibold">{currentQuestion.question_text}</p>
                </div>
                <div className="space-y-4">
                    {currentQuestion.options.map((option, index) => (
                        <button
                            key={index}
                            onClick={() => handleOptionSelect(index)}
                            className={`w-full text-left p-4 rounded-lg border-2 ${selectedOption === index ? 'bg-blue-100 border-blue-500' : 'bg-white border-gray-300 hover:bg-gray-100'}`}
                        >
                            {option.text}
                        </button>
                    ))}
                </div>
                <div className="flex justify-between items-center mt-8">
                    <span>{`Question ${currentQuestionIndex + 1} of ${quiz.questions.length}`}</span>
                    {currentQuestionIndex < quiz.questions.length - 1 ? (
                        <button onClick={handleNext} className="bg-blue-500 text-white font-bold py-2 px-4 rounded">
                            Next
                        </button>
                    ) : (
                        <button onClick={handleSubmit} className="bg-green-500 text-white font-bold py-2 px-4 rounded">
                            Submit
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default QuizPage;
