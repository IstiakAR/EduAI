"""
Gemini AI service for question generation and evaluation.
"""
import json
import asyncio
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from app.core.config import get_settings
from app.schemas.question import QuestionType, Difficulty, QuestionCreate, MCQOption

settings = get_settings()

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


class GeminiService:
    """Service for interacting with Gemini AI."""
    
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
    
    async def generate_questions(
        self,
        subject: str,
        topic: str,
        difficulty: Difficulty,
        question_type: QuestionType,
        num_questions: int = 5,
        additional_context: str = None
    ) -> List[QuestionCreate]:
        """Generate questions using Gemini AI."""
        
        prompt = self._build_question_generation_prompt(
            subject, topic, difficulty, question_type, num_questions, additional_context
        )
        
        try:
            response = await self._call_gemini_async(prompt)
            questions = self._parse_questions_response(response, subject, topic, difficulty, question_type)
            return questions
        except Exception as e:
            raise Exception(f"Question generation failed: {str(e)}")
    
    async def evaluate_answer(
        self,
        question: str,
        correct_answer: str,
        user_answer: str,
        question_type: QuestionType,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Evaluate a user's answer using Gemini AI."""
        
        if question_type == QuestionType.MCQ:
            return self._evaluate_mcq_answer(correct_answer, user_answer)
        
        prompt = self._build_evaluation_prompt(question, correct_answer, user_answer, question_type, context)
        
        try:
            response = await self._call_gemini_async(prompt)
            evaluation = self._parse_evaluation_response(response)
            return evaluation
        except Exception as e:
            raise Exception(f"Answer evaluation failed: {str(e)}")
    
    async def generate_explanation(
        self,
        question: str,
        correct_answer: str,
        user_answer: str = None,
        context: Dict[str, Any] = None
    ) -> str:
        """Generate explanation for a question and answer."""
        
        prompt = self._build_explanation_prompt(question, correct_answer, user_answer, context)
        
        try:
            response = await self._call_gemini_async(prompt)
            return response.strip()
        except Exception as e:
            raise Exception(f"Explanation generation failed: {str(e)}")
    
    async def improve_question_difficulty(
        self,
        question: str,
        current_difficulty: Difficulty,
        target_difficulty: Difficulty,
        subject: str,
        topic: str
    ) -> str:
        """Improve question difficulty based on adaptive learning."""
        
        prompt = f"""
        Modify the following {current_difficulty.value} level question to be {target_difficulty.value} level for {subject} - {topic}:
        
        Original Question: {question}
        
        Please provide only the modified question text that maintains the same learning objective but adjusts the difficulty level appropriately.
        """
        
        try:
            response = await self._call_gemini_async(prompt)
            return response.strip()
        except Exception as e:
            raise Exception(f"Question difficulty adjustment failed: {str(e)}")
    
    def _build_question_generation_prompt(
        self,
        subject: str,
        topic: str,
        difficulty: Difficulty,
        question_type: QuestionType,
        num_questions: int,
        additional_context: str = None
    ) -> str:
        """Build prompt for question generation."""
        
        context_section = f"\nAdditional Context: {additional_context}" if additional_context else ""
        
        if question_type == QuestionType.MCQ:
            format_instructions = """
            For each question, provide:
            1. Question text
            2. Four options (A, B, C, D)
            3. Correct answer (A, B, C, or D)
            4. Brief explanation
            
            Format as JSON:
            {
                "questions": [
                    {
                        "question_text": "...",
                        "options": [
                            {"option_id": "A", "text": "...", "is_correct": false},
                            {"option_id": "B", "text": "...", "is_correct": true},
                            {"option_id": "C", "text": "...", "is_correct": false},
                            {"option_id": "D", "text": "...", "is_correct": false}
                        ],
                        "explanation": "..."
                    }
                ]
            }
            """
        elif question_type == QuestionType.SHORT:
            format_instructions = """
            For each question, provide:
            1. Question text (expecting 1-3 sentence answers)
            2. Model answer
            3. Key points for evaluation
            
            Format as JSON:
            {
                "questions": [
                    {
                        "question_text": "...",
                        "correct_answer": "...",
                        "explanation": "Key points: ..."
                    }
                ]
            }
            """
        else:  # LONG
            format_instructions = """
            For each question, provide:
            1. Question text (expecting paragraph-length answers)
            2. Comprehensive model answer
            3. Evaluation criteria
            
            Format as JSON:
            {
                "questions": [
                    {
                        "question_text": "...",
                        "correct_answer": "...",
                        "explanation": "Evaluation criteria: ..."
                    }
                ]
            }
            """
        
        prompt = f"""
        Generate {num_questions} {difficulty.value} level {question_type.value} questions for {subject} - {topic}.
        
        Requirements:
        - Questions should be educationally sound and test understanding
        - Difficulty level: {difficulty.value}
        - Subject: {subject}
        - Topic: {topic}
        - Avoid ambiguous or trick questions
        - Ensure questions are factually accurate{context_section}
        
        {format_instructions}
        
        Provide only the JSON response, no additional text.
        """
        
        return prompt
    
    def _build_evaluation_prompt(
        self,
        question: str,
        correct_answer: str,
        user_answer: str,
        question_type: QuestionType,
        context: Dict[str, Any] = None
    ) -> str:
        """Build prompt for answer evaluation."""
        
        context_section = ""
        if context:
            context_section = f"\nAdditional Context: {json.dumps(context, indent=2)}"
        
        prompt = f"""
        Evaluate the following student answer for a {question_type.value} question:
        
        Question: {question}
        Model Answer: {correct_answer}
        Student Answer: {user_answer}{context_section}
        
        Please provide evaluation in JSON format:
        {{
            "score": <float between 0.0 and 1.0>,
            "is_correct": <boolean>,
            "feedback": "<detailed feedback for the student>",
            "strengths": ["<list of strengths in the answer>"],
            "improvements": ["<list of areas for improvement>"],
            "partial_credit_reason": "<explanation if partial credit given>"
        }}
        
        Evaluation criteria:
        - Accuracy of information
        - Completeness of answer
        - Understanding demonstrated
        - Clarity of explanation
        - Use of appropriate terminology
        
        Provide only the JSON response, no additional text.
        """
        
        return prompt
    
    def _build_explanation_prompt(
        self,
        question: str,
        correct_answer: str,
        user_answer: str = None,
        context: Dict[str, Any] = None
    ) -> str:
        """Build prompt for explanation generation."""
        
        user_section = f"\nStudent's Answer: {user_answer}" if user_answer else ""
        context_section = f"\nContext: {json.dumps(context, indent=2)}" if context else ""
        
        prompt = f"""
        Provide a clear, educational explanation for the following question and answer:
        
        Question: {question}
        Correct Answer: {correct_answer}{user_section}{context_section}
        
        The explanation should:
        - Explain why the correct answer is correct
        - Provide relevant background concepts
        - Be educational and help student learning
        - Use clear, accessible language
        - Include examples if helpful
        
        Provide a concise but comprehensive explanation.
        """
        
        return prompt
    
    async def _call_gemini_async(self, prompt: str) -> str:
        """Make async call to Gemini API."""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
        )
        return response.text
    
    def _parse_questions_response(
        self,
        response: str,
        subject: str,
        topic: str,
        difficulty: Difficulty,
        question_type: QuestionType
    ) -> List[QuestionCreate]:
        """Parse Gemini response into QuestionCreate objects."""
        try:
            # Clean response and extract JSON
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            
            data = json.loads(clean_response)
            questions = []
            
            for q_data in data.get("questions", []):
                question = QuestionCreate(
                    question_text=q_data["question_text"],
                    question_type=question_type,
                    subject=subject,
                    topic=topic,
                    difficulty=difficulty,
                    explanation=q_data.get("explanation"),
                    correct_answer=q_data.get("correct_answer")
                )
                
                # Handle MCQ options
                if question_type == QuestionType.MCQ and "options" in q_data:
                    options = []
                    for opt in q_data["options"]:
                        options.append(MCQOption(
                            option_id=opt["option_id"],
                            text=opt["text"],
                            is_correct=opt["is_correct"]
                        ))
                    question.options = options
                
                questions.append(question)
            
            return questions
        
        except (json.JSONDecodeError, KeyError) as e:
            raise Exception(f"Failed to parse questions response: {str(e)}")
    
    def _parse_evaluation_response(self, response: str) -> Dict[str, Any]:
        """Parse Gemini evaluation response."""
        try:
            # Clean response and extract JSON
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            
            return json.loads(clean_response)
        
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse evaluation response: {str(e)}")
    
    def _evaluate_mcq_answer(self, correct_answer: str, user_answer: str) -> Dict[str, Any]:
        """Evaluate MCQ answer."""
        is_correct = correct_answer.upper() == user_answer.upper()
        
        return {
            "score": 1.0 if is_correct else 0.0,
            "is_correct": is_correct,
            "feedback": "Correct!" if is_correct else f"Incorrect. The correct answer is {correct_answer}.",
            "strengths": ["Selected the correct option"] if is_correct else [],
            "improvements": [] if is_correct else ["Review the topic and try again"],
            "partial_credit_reason": ""
        }


# Global service instance
gemini_service = GeminiService()