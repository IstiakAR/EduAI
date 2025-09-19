"""
AI Assistant service for answering academic questions.
"""
import asyncio
import httpx
from typing import Dict, Any, List, Optional
from app.services.gemini_service import gemini_service
from app.core.config import get_settings

settings = get_settings()


class AssistantService:
    """Service for AI-powered academic assistance."""
    
    def __init__(self):
        self.wikipedia_base_url = settings.WIKIPEDIA_API_URL
    
    async def answer_question(
        self,
        question: str,
        subject: str = None,
        context: Dict[str, Any] = None,
        use_web_search: bool = True
    ) -> Dict[str, Any]:
        """Answer an academic question using AI and web resources."""
        
        try:
            # First, try to get context from Wikipedia if needed
            wikipedia_context = ""
            if use_web_search:
                wikipedia_context = await self._search_wikipedia(question, subject)
            
            # Build comprehensive prompt
            prompt = self._build_answer_prompt(question, subject, context, wikipedia_context)
            
            # Get AI response
            ai_response = await gemini_service._call_gemini_async(prompt)
            
            # Format response
            result = {
                "question": question,
                "answer": ai_response.strip(),
                "sources": [],
                "confidence": "high",  # Could be calculated based on various factors
                "subject": subject,
                "related_topics": await self._extract_related_topics(ai_response),
                "follow_up_questions": await self._generate_follow_up_questions(question, subject)
            }
            
            # Add Wikipedia sources if used
            if wikipedia_context:
                result["sources"].append({
                    "type": "wikipedia",
                    "description": "Wikipedia articles related to the query"
                })
            
            return result
            
        except Exception as e:
            raise Exception(f"Question answering failed: {str(e)}")
    
    async def explain_concept(
        self,
        concept: str,
        subject: str,
        level: str = "intermediate",
        include_examples: bool = True
    ) -> Dict[str, Any]:
        """Explain a specific concept in detail."""
        
        prompt = f"""
        Explain the concept of "{concept}" in {subject} for a {level} level student.
        
        Please provide:
        1. Clear definition
        2. Key characteristics or properties
        3. How it relates to other concepts
        4. Real-world applications or significance
        {"5. Practical examples" if include_examples else ""}
        
        Make the explanation educational, engaging, and appropriate for the specified level.
        """
        
        try:
            explanation = await gemini_service._call_gemini_async(prompt)
            
            return {
                "concept": concept,
                "subject": subject,
                "level": level,
                "explanation": explanation.strip(),
                "key_points": await self._extract_key_points(explanation),
                "related_concepts": await self._find_related_concepts(concept, subject)
            }
            
        except Exception as e:
            raise Exception(f"Concept explanation failed: {str(e)}")
    
    async def get_study_suggestions(
        self,
        subject: str,
        topics: List[str],
        difficulty_level: str = "medium",
        learning_goals: List[str] = None,
        time_available_minutes: int = 60
    ) -> Dict[str, Any]:
        """Generate personalized study suggestions."""
        
        goals_section = ""
        if learning_goals:
            goals_section = f"\nLearning Goals: {', '.join(learning_goals)}"
        
        prompt = f"""
        Create a personalized study plan for:
        Subject: {subject}
        Topics: {', '.join(topics)}
        Difficulty Level: {difficulty_level}
        Available Time: {time_available_minutes} minutes{goals_section}
        
        Please provide:
        1. Prioritized study order
        2. Time allocation for each topic
        3. Recommended study methods
        4. Key concepts to focus on
        5. Practice activities suggestions
        6. Assessment checkpoints
        
        Make it practical and achievable within the given timeframe.
        """
        
        try:
            suggestions = await gemini_service._call_gemini_async(prompt)
            
            return {
                "subject": subject,
                "topics": topics,
                "difficulty_level": difficulty_level,
                "time_available_minutes": time_available_minutes,
                "study_plan": suggestions.strip(),
                "estimated_completion_time": time_available_minutes,
                "recommended_resources": await self._get_study_resources(subject, topics)
            }
            
        except Exception as e:
            raise Exception(f"Study suggestions generation failed: {str(e)}")
    
    async def solve_problem_step_by_step(
        self,
        problem: str,
        subject: str,
        show_work: bool = True
    ) -> Dict[str, Any]:
        """Solve a problem with step-by-step explanation."""
        
        prompt = f"""
        Solve the following {subject} problem step by step:
        
        Problem: {problem}
        
        Please provide:
        1. Clear identification of what's being asked
        2. Step-by-step solution with explanations
        3. Final answer
        4. Verification of the answer (if applicable)
        
        {"Show all work and reasoning for each step." if show_work else "Focus on key steps and final answer."}
        """
        
        try:
            solution = await gemini_service._call_gemini_async(prompt)
            
            return {
                "problem": problem,
                "subject": subject,
                "solution": solution.strip(),
                "steps": await self._extract_solution_steps(solution),
                "key_concepts_used": await self._identify_concepts_used(problem, subject)
            }
            
        except Exception as e:
            raise Exception(f"Problem solving failed: {str(e)}")
    
    async def _search_wikipedia(self, query: str, subject: str = None) -> str:
        """Search Wikipedia for relevant information."""
        
        try:
            search_query = f"{query} {subject}" if subject else query
            
            async with httpx.AsyncClient() as client:
                # Search for articles
                search_url = f"{self.wikipedia_base_url}/page/summary/{search_query.replace(' ', '_')}"
                response = await client.get(search_url)
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("extract", "")[:1000]  # Limit to 1000 chars
                
        except Exception:
            pass  # Fail silently and continue without Wikipedia context
        
        return ""
    
    def _build_answer_prompt(
        self,
        question: str,
        subject: str = None,
        context: Dict[str, Any] = None,
        wikipedia_context: str = ""
    ) -> str:
        """Build prompt for answering questions."""
        
        subject_section = f"\nSubject Context: {subject}" if subject else ""
        context_section = ""
        if context:
            context_section = f"\nAdditional Context: {context}"
        wikipedia_section = f"\nWikipedia Context: {wikipedia_context}" if wikipedia_context else ""
        
        prompt = f"""
        Please answer the following academic question comprehensively and accurately:
        
        Question: {question}{subject_section}{context_section}{wikipedia_section}
        
        Provide a clear, educational answer that:
        1. Directly addresses the question
        2. Includes relevant background information
        3. Uses appropriate academic language
        4. Cites key concepts and principles
        5. Provides examples when helpful
        6. Is factually accurate and up-to-date
        
        If the question is ambiguous, clarify your interpretation and provide the most helpful answer.
        """
        
        return prompt
    
    async def _extract_related_topics(self, response: str) -> List[str]:
        """Extract related topics from AI response."""
        
        prompt = f"""
        From the following text, extract 3-5 related topics or concepts that a student might want to explore further:
        
        Text: {response[:500]}...
        
        Provide only a list of topics, one per line.
        """
        
        try:
            topics_response = await gemini_service._call_gemini_async(prompt)
            topics = [topic.strip() for topic in topics_response.split('\n') if topic.strip()]
            return topics[:5]  # Limit to 5 topics
        except:
            return []
    
    async def _generate_follow_up_questions(self, original_question: str, subject: str = None) -> List[str]:
        """Generate follow-up questions related to the original question."""
        
        subject_section = f" in {subject}" if subject else ""
        
        prompt = f"""
        Based on this question: "{original_question}"
        
        Generate 3 thoughtful follow-up questions that would help a student deepen their understanding{subject_section}.
        
        Provide only the questions, one per line.
        """
        
        try:
            questions_response = await gemini_service._call_gemini_async(prompt)
            questions = [q.strip() for q in questions_response.split('\n') if q.strip() and '?' in q]
            return questions[:3]  # Limit to 3 questions
        except:
            return []
    
    async def _extract_key_points(self, explanation: str) -> List[str]:
        """Extract key points from an explanation."""
        
        prompt = f"""
        Extract 3-5 key points from this explanation:
        
        {explanation}
        
        Provide only the key points, one per line.
        """
        
        try:
            points_response = await gemini_service._call_gemini_async(prompt)
            points = [point.strip() for point in points_response.split('\n') if point.strip()]
            return points[:5]
        except:
            return []
    
    async def _find_related_concepts(self, concept: str, subject: str) -> List[str]:
        """Find concepts related to the given concept."""
        
        prompt = f"""
        List 4-6 concepts in {subject} that are closely related to "{concept}".
        
        Provide only the concept names, one per line.
        """
        
        try:
            concepts_response = await gemini_service._call_gemini_async(prompt)
            concepts = [concept.strip() for concept in concepts_response.split('\n') if concept.strip()]
            return concepts[:6]
        except:
            return []
    
    async def _get_study_resources(self, subject: str, topics: List[str]) -> List[Dict[str, str]]:
        """Get recommended study resources."""
        
        # This would typically integrate with educational resource APIs
        # For now, return generic suggestions
        return [
            {"type": "textbook", "description": f"Standard {subject} textbook covering {', '.join(topics[:2])}"},
            {"type": "online_course", "description": f"Online course materials for {subject}"},
            {"type": "practice_problems", "description": f"Practice exercises for {', '.join(topics)}"},
            {"type": "video_lectures", "description": f"Video explanations of key {subject} concepts"}
        ]
    
    async def _extract_solution_steps(self, solution: str) -> List[str]:
        """Extract solution steps from a step-by-step solution."""
        
        # Simple extraction - look for numbered steps or clear step markers
        steps = []
        lines = solution.split('\n')
        
        for line in lines:
            line = line.strip()
            if (line.startswith(('1.', '2.', '3.', '4.', '5.', 'Step 1', 'Step 2', 'Step 3')) or
                'step' in line.lower()):
                steps.append(line)
        
        return steps[:10]  # Limit to 10 steps
    
    async def _identify_concepts_used(self, problem: str, subject: str) -> List[str]:
        """Identify key concepts used in solving a problem."""
        
        prompt = f"""
        For this {subject} problem: "{problem}"
        
        List the key mathematical/scientific concepts or principles that would be used to solve it.
        
        Provide only the concept names, one per line.
        """
        
        try:
            concepts_response = await gemini_service._call_gemini_async(prompt)
            concepts = [concept.strip() for concept in concepts_response.split('\n') if concept.strip()]
            return concepts[:5]
        except:
            return []


# Global service instance
assistant_service = AssistantService()