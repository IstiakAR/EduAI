"""
Evaluation service for AI-powered answer assessment.
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.services.gemini_service import gemini_service
from app.db.crud import answer_crud, result_crud, progress_crud
from app.schemas.question import QuestionType


class EvaluationService:
    """Service for evaluating answers and calculating scores."""
    
    async def evaluate_single_answer(
        self,
        question_id: str,
        question_text: str,
        question_type: QuestionType,
        correct_answer: str,
        user_answer: str,
        user_id: str,
        points: int = 1,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Evaluate a single answer."""
        
        # Get AI evaluation
        evaluation = await gemini_service.evaluate_answer(
            question=question_text,
            correct_answer=correct_answer,
            user_answer=user_answer,
            question_type=question_type,
            context=context
        )
        
        # Calculate final score
        final_score = evaluation["score"] * points
        
        # Store answer in database
        answer_data = {
            "question_id": question_id,
            "user_id": user_id,
            "answer_text": user_answer,
            "is_correct": evaluation["is_correct"],
            "score": final_score,
            "feedback": evaluation["feedback"]
        }
        
        stored_answer = await answer_crud.create_answer(answer_data)
        
        # Prepare response
        result = {
            "answer_id": stored_answer["id"],
            "score": final_score,
            "max_score": points,
            "is_correct": evaluation["is_correct"],
            "feedback": evaluation["feedback"],
            "strengths": evaluation.get("strengths", []),
            "improvements": evaluation.get("improvements", []),
            "partial_credit_reason": evaluation.get("partial_credit_reason", "")
        }
        
        return result
    
    async def evaluate_exam_submission(
        self,
        exam_id: str,
        user_id: str,
        answers: List[Dict[str, Any]],
        time_taken_minutes: Optional[int] = None
    ) -> Dict[str, Any]:
        """Evaluate a complete exam submission."""
        
        total_score = 0.0
        max_score = 0.0
        correct_answers = 0
        evaluation_results = []
        
        # Evaluate each answer
        for answer_data in answers:
            question_id = answer_data["question_id"]
            user_answer = answer_data["answer_text"]
            
            # Get question details (you would fetch this from database)
            # For now, assuming it's provided in answer_data
            question_text = answer_data.get("question_text", "")
            question_type = QuestionType(answer_data.get("question_type", "mcq"))
            correct_answer = answer_data.get("correct_answer", "")
            points = answer_data.get("points", 1)
            
            evaluation = await self.evaluate_single_answer(
                question_id=question_id,
                question_text=question_text,
                question_type=question_type,
                correct_answer=correct_answer,
                user_answer=user_answer,
                user_id=user_id,
                points=points
            )
            
            total_score += evaluation["score"]
            max_score += points
            if evaluation["is_correct"]:
                correct_answers += 1
            
            evaluation_results.append({
                "question_id": question_id,
                "answer_id": evaluation["answer_id"],
                "score": evaluation["score"],
                "max_score": points,
                "is_correct": evaluation["is_correct"],
                "feedback": evaluation["feedback"]
            })
        
        # Calculate percentage
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        # Analyze strengths and weaknesses
        strengths, weaknesses = await self._analyze_performance(evaluation_results, answers)
        
        # Store result in database
        result_data = {
            "user_id": user_id,
            "exam_id": exam_id,
            "total_questions": len(answers),
            "correct_answers": correct_answers,
            "total_score": total_score,
            "max_score": max_score,
            "percentage": percentage,
            "time_taken_minutes": time_taken_minutes,
            "subject": answers[0].get("subject", "") if answers else "",
            "difficulty": answers[0].get("difficulty", "") if answers else "",
            "topics_covered": list(set([ans.get("topic", "") for ans in answers if ans.get("topic")])),
            "strengths": strengths,
            "weaknesses": weaknesses
        }
        
        stored_result = await result_crud.create_result(result_data)
        
        # Update user progress
        await self._update_user_progress(user_id, result_data, evaluation_results)
        
        return {
            "result_id": stored_result["id"],
            "total_questions": len(answers),
            "correct_answers": correct_answers,
            "total_score": total_score,
            "max_score": max_score,
            "percentage": percentage,
            "time_taken_minutes": time_taken_minutes,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "question_results": evaluation_results,
            "overall_feedback": await self._generate_overall_feedback(percentage, strengths, weaknesses)
        }
    
    async def batch_evaluate_answers(
        self,
        user_id: str,
        answer_batch: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Evaluate multiple answers in batch."""
        
        tasks = []
        for answer_data in answer_batch:
            task = self.evaluate_single_answer(
                question_id=answer_data["question_id"],
                question_text=answer_data["question_text"],
                question_type=QuestionType(answer_data["question_type"]),
                correct_answer=answer_data["correct_answer"],
                user_answer=answer_data["user_answer"],
                user_id=user_id,
                points=answer_data.get("points", 1),
                context=answer_data.get("context")
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
    
    async def _analyze_performance(
        self,
        evaluation_results: List[Dict[str, Any]],
        answers: List[Dict[str, Any]]
    ) -> tuple[List[str], List[str]]:
        """Analyze performance to identify strengths and weaknesses."""
        
        strengths = []
        weaknesses = []
        
        # Group by topic/subject for analysis
        topic_performance = {}
        for i, result in enumerate(evaluation_results):
            topic = answers[i].get("topic", "Unknown")
            if topic not in topic_performance:
                topic_performance[topic] = {"correct": 0, "total": 0}
            
            topic_performance[topic]["total"] += 1
            if result["is_correct"]:
                topic_performance[topic]["correct"] += 1
        
        # Identify strengths (>= 80% accuracy)
        for topic, perf in topic_performance.items():
            accuracy = perf["correct"] / perf["total"]
            if accuracy >= 0.8:
                strengths.append(f"Strong understanding of {topic} (${accuracy:.0%} accuracy)")
            elif accuracy < 0.5:
                weaknesses.append(f"Needs improvement in {topic} ({accuracy:.0%} accuracy)")
        
        return strengths, weaknesses
    
    async def _update_user_progress(
        self,
        user_id: str,
        result_data: Dict[str, Any],
        evaluation_results: List[Dict[str, Any]]
    ) -> None:
        """Update user progress based on exam results."""
        
        subject = result_data["subject"]
        
        # Get or create progress record
        progress = await progress_crud.get_or_create_progress(user_id, subject)
        
        # Calculate updates
        questions_attempted = result_data["total_questions"]
        questions_correct = result_data["correct_answers"]
        score_gained = result_data["total_score"]
        
        # Update progress
        update_data = {
            "total_questions_attempted": progress["total_questions_attempted"] + questions_attempted,
            "total_questions_correct": progress["total_questions_correct"] + questions_correct,
            "total_score": progress["total_score"] + score_gained,
            "last_activity": datetime.utcnow().isoformat()
        }
        
        # Recalculate average accuracy
        new_total_attempted = update_data["total_questions_attempted"]
        new_total_correct = update_data["total_questions_correct"]
        update_data["average_accuracy"] = (new_total_correct / new_total_attempted) if new_total_attempted > 0 else 0
        
        # Update streak
        if result_data["percentage"] >= 70:  # Consider 70% as good performance
            update_data["streak_count"] = progress["streak_count"] + 1
            update_data["best_streak"] = max(progress["best_streak"], update_data["streak_count"])
        else:
            update_data["streak_count"] = 0
        
        # Calculate gamification points (example logic)
        points_earned = int(result_data["total_score"] * 10)  # 10 points per score point
        update_data["total_points"] = progress["total_points"] + points_earned
        
        # Level calculation (example: 1000 points per level)
        new_level = (update_data["total_points"] // 1000) + 1
        update_data["level"] = new_level
        
        await progress_crud.update_progress(progress["id"], update_data)
    
    async def _generate_overall_feedback(
        self,
        percentage: float,
        strengths: List[str],
        weaknesses: List[str]
    ) -> str:
        """Generate overall feedback for the exam result."""
        
        if percentage >= 90:
            performance_msg = "Excellent performance! You demonstrate strong mastery of the material."
        elif percentage >= 80:
            performance_msg = "Good work! You have a solid understanding with room for minor improvements."
        elif percentage >= 70:
            performance_msg = "Fair performance. You understand the basics but need to strengthen some areas."
        elif percentage >= 60:
            performance_msg = "You're on the right track, but there's significant room for improvement."
        else:
            performance_msg = "This topic needs more study. Consider reviewing the fundamentals."
        
        feedback_parts = [performance_msg]
        
        if strengths:
            feedback_parts.append(f"Your strengths include: {', '.join(strengths[:3])}")
        
        if weaknesses:
            feedback_parts.append(f"Focus on improving: {', '.join(weaknesses[:3])}")
        
        feedback_parts.append("Keep practicing to improve your understanding!")
        
        return " ".join(feedback_parts)


# Global service instance
evaluation_service = EvaluationService()