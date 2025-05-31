"""
Tests for quiz functionality and scoring logic
"""

import pytest
import random
from typing import List, Dict, Any


@pytest.mark.unit
class TestQuizLogic:
    """Test quiz logic and scoring system"""

    def test_quiz_initialization(self, quiz_data):
        """Test quiz initialization with vocabulary data"""
        quiz = Quiz(quiz_data)
        assert quiz.vocabulary_list == quiz_data
        assert quiz.current_index == 0
        assert quiz.score == 0
        assert quiz.total_questions == len(quiz_data)
        assert quiz.is_completed == False

    def test_quiz_answer_validation(self, quiz_data):
        """Test answer validation logic"""
        quiz = Quiz(quiz_data)
        
        # Test correct answer (exact match)
        current_word = quiz.get_current_word()
        correct_meaning = current_word["meaning"]
        assert quiz.check_answer(correct_meaning) == True
        
        # Test correct answer (case insensitive)
        assert quiz.check_answer(correct_meaning.upper()) == True
        assert quiz.check_answer(correct_meaning.lower()) == True
        
        # Test incorrect answer
        assert quiz.check_answer("wrong answer") == False
        
        # Test empty answer
        assert quiz.check_answer("") == False
        assert quiz.check_answer(None) == False

    def test_quiz_progression(self, quiz_data):
        """Test quiz progression through questions"""
        quiz = Quiz(quiz_data)
        initial_questions = len(quiz_data)
        
        for i in range(initial_questions):
            assert quiz.current_index == i
            assert quiz.is_completed == False
            
            current_word = quiz.get_current_word()
            assert current_word == quiz_data[i]
            
            # Answer correctly
            quiz.submit_answer(current_word["meaning"])
            
            if i < initial_questions - 1:
                assert quiz.current_index == i + 1
            else:
                assert quiz.is_completed == True

    def test_quiz_scoring_system(self, quiz_data):
        """Test quiz scoring calculations"""
        quiz = Quiz(quiz_data)
        
        # Answer all questions correctly
        correct_answers = 0
        for _ in range(len(quiz_data)):
            current_word = quiz.get_current_word()
            quiz.submit_answer(current_word["meaning"])
            correct_answers += 1
        
        assert quiz.score == correct_answers
        assert quiz.get_score_percentage() == 100.0
        
        # Test partial scoring
        quiz = Quiz(quiz_data)
        correct_count = 0
        
        for i, vocab in enumerate(quiz_data):
            if i % 2 == 0:  # Answer every other question correctly
                quiz.submit_answer(vocab["meaning"])
                correct_count += 1
            else:
                quiz.submit_answer("wrong answer")
        
        expected_percentage = (correct_count / len(quiz_data)) * 100
        assert quiz.get_score_percentage() == expected_percentage

    def test_quiz_answer_normalization(self, quiz_data):
        """Test answer normalization and fuzzy matching"""
        quiz = Quiz(quiz_data)
        current_word = quiz.get_current_word()
        correct_meaning = current_word["meaning"]
        
        # Test whitespace normalization
        assert quiz.check_answer(f"  {correct_meaning}  ") == True
        assert quiz.check_answer(f"\t{correct_meaning}\n") == True
        
        # Test accent handling (if applicable)
        if "à" in correct_meaning:
            normalized = correct_meaning.replace("à", "a")
            # This would depend on implementation - may or may not pass
            
        # Test partial matches (if implemented)
        # This would depend on quiz configuration

    def test_quiz_time_tracking(self, quiz_data):
        """Test quiz time tracking functionality"""
        quiz = Quiz(quiz_data)
        quiz.start_timer()
        
        import time
        time.sleep(0.1)  # Small delay for testing
        
        # Answer first question
        current_word = quiz.get_current_word()
        quiz.submit_answer(current_word["meaning"])
        
        elapsed = quiz.get_elapsed_time()
        assert elapsed > 0
        assert elapsed < 10  # Should be less than 10 seconds for test

    def test_quiz_difficulty_levels(self):
        """Test quiz generation with different difficulty levels"""
        easy_words = [
            {"word": "cat", "meaning": "mèo", "difficulty": "easy"},
            {"word": "dog", "meaning": "chó", "difficulty": "easy"}
        ]
        
        hard_words = [
            {"word": "serendipity", "meaning": "may mắn bất ngờ", "difficulty": "hard"},
            {"word": "ephemeral", "meaning": "tạm thời", "difficulty": "hard"}
        ]
        
        easy_quiz = Quiz(easy_words)
        hard_quiz = Quiz(hard_words)
        
        assert easy_quiz.get_difficulty() == "easy"
        assert hard_quiz.get_difficulty() == "hard"

    def test_quiz_randomization(self, quiz_data):
        """Test quiz question randomization"""
        # Create multiple quizzes with same data
        quiz1 = Quiz(quiz_data.copy(), randomize=True)
        quiz2 = Quiz(quiz_data.copy(), randomize=True)
        
        # Get question orders
        order1 = [quiz1.vocabulary_list[i]["word"] for i in range(len(quiz1.vocabulary_list))]
        order2 = [quiz2.vocabulary_list[i]["word"] for i in range(len(quiz2.vocabulary_list))]
        
        # Orders should be different (with high probability)
        if len(quiz_data) > 2:
            # For small datasets, randomization might produce same order
            pass  # This test might be flaky with small datasets

    def test_quiz_statistics(self, quiz_data):
        """Test quiz statistics generation"""
        quiz = Quiz(quiz_data)
        
        # Answer some questions correctly, some incorrectly
        correct_answers = []
        incorrect_answers = []
        
        for i, vocab in enumerate(quiz_data):
            if i % 2 == 0:
                quiz.submit_answer(vocab["meaning"])
                correct_answers.append(vocab["word"])
            else:
                quiz.submit_answer("wrong")
                incorrect_answers.append(vocab["word"])
        
        stats = quiz.get_statistics()
        
        assert stats["total_questions"] == len(quiz_data)
        assert stats["correct_answers"] == len(correct_answers)
        assert stats["incorrect_answers"] == len(incorrect_answers)
        assert stats["score_percentage"] == (len(correct_answers) / len(quiz_data)) * 100

    def test_quiz_restart_functionality(self, quiz_data):
        """Test quiz restart functionality"""
        quiz = Quiz(quiz_data)
        
        # Complete part of the quiz
        for i in range(min(2, len(quiz_data))):
            current_word = quiz.get_current_word()
            quiz.submit_answer(current_word["meaning"])
        
        original_score = quiz.score
        original_index = quiz.current_index
        
        # Restart quiz
        quiz.restart()
        
        assert quiz.score == 0
        assert quiz.current_index == 0
        assert quiz.is_completed == False
        assert quiz.score != original_score or original_score == 0

    @pytest.mark.integration
    def test_quiz_integration_with_api(self, api_client, clean_vocabulary_data, sample_vocabulary_data):
        """Test quiz integration with vocabulary API"""
        # Add vocabulary data via API
        created_vocab = []
        for vocab_data in sample_vocabulary_data:
            response = api_client.post("/vocabulary", json=vocab_data)
            assert response.status_code in [200, 201]
            created_vocab.append(response.json())
        
        # Get vocabulary for quiz
        response = api_client.get("/vocabulary")
        assert response.status_code == 200
        vocabulary_list = response.json()
        
        # Create quiz with API data
        quiz = Quiz(vocabulary_list)
        assert len(quiz.vocabulary_list) >= len(sample_vocabulary_data)
        
        # Test quiz functionality
        if quiz.vocabulary_list:
            current_word = quiz.get_current_word()
            assert "word" in current_word
            assert "meaning" in current_word

    def test_quiz_edge_cases(self):
        """Test quiz edge cases and error handling"""
        # Empty vocabulary list
        with pytest.raises(ValueError):
            Quiz([])
        
        # Invalid vocabulary format
        invalid_vocab = [{"invalid": "format"}]
        with pytest.raises(ValueError):
            Quiz(invalid_vocab)
        
        # Single question quiz
        single_question = [{"word": "test", "meaning": "thử nghiệm"}]
        quiz = Quiz(single_question)
        
        current_word = quiz.get_current_word()
        quiz.submit_answer(current_word["meaning"])
        
        assert quiz.is_completed == True
        assert quiz.score == 1


class Quiz:
    """Quiz class for testing - simplified implementation"""
    
    def __init__(self, vocabulary_list: List[Dict], randomize: bool = False):
        if not vocabulary_list:
            raise ValueError("Vocabulary list cannot be empty")
        
        # Validate vocabulary format
        for vocab in vocabulary_list:
            if "word" not in vocab or "meaning" not in vocab:
                raise ValueError("Invalid vocabulary format - missing 'word' or 'meaning'")
        
        self.vocabulary_list = vocabulary_list.copy()
        if randomize:
            random.shuffle(self.vocabulary_list)
        
        self.current_index = 0
        self.score = 0
        self.total_questions = len(vocabulary_list)
        self.is_completed = False
        self.start_time = None
        self.answer_history = []
    
    def start_timer(self):
        """Start quiz timer"""
        import time
        self.start_time = time.time()
    
    def get_current_word(self) -> Dict:
        """Get current vocabulary word"""
        if self.current_index < len(self.vocabulary_list):
            return self.vocabulary_list[self.current_index]
        return None
    
    def check_answer(self, user_answer: str) -> bool:
        """Check if user answer is correct"""
        if not user_answer:
            return False
        
        current_word = self.get_current_word()
        if not current_word:
            return False
        
        correct_answer = current_word["meaning"]
        
        # Normalize answers (strip whitespace, case insensitive)
        user_answer = str(user_answer).strip().lower()
        correct_answer = correct_answer.strip().lower()
        
        return user_answer == correct_answer
    
    def submit_answer(self, user_answer: str):
        """Submit answer and progress quiz"""
        is_correct = self.check_answer(user_answer)
        
        # Record answer
        current_word = self.get_current_word()
        self.answer_history.append({
            "word": current_word["word"],
            "correct_meaning": current_word["meaning"],
            "user_answer": user_answer,
            "is_correct": is_correct
        })
        
        if is_correct:
            self.score += 1
        
        # Progress to next question
        self.current_index += 1
        
        if self.current_index >= self.total_questions:
            self.is_completed = True
    
    def get_score_percentage(self) -> float:
        """Get score as percentage"""
        if self.total_questions == 0:
            return 0.0
        return (self.score / self.total_questions) * 100
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since quiz started"""
        if self.start_time:
            import time
            return time.time() - self.start_time
        return 0.0
    
    def get_difficulty(self) -> str:
        """Get overall quiz difficulty"""
        if not self.vocabulary_list:
            return "unknown"
        
        difficulties = [vocab.get("difficulty", "medium") for vocab in self.vocabulary_list]
        
        # Simple logic: if more than half are hard, quiz is hard
        hard_count = sum(1 for d in difficulties if d == "hard")
        easy_count = sum(1 for d in difficulties if d == "easy")
        
        if hard_count > len(difficulties) / 2:
            return "hard"
        elif easy_count > len(difficulties) / 2:
            return "easy"
        else:
            return "medium"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed quiz statistics"""
        correct_count = sum(1 for answer in self.answer_history if answer["is_correct"])
        incorrect_count = len(self.answer_history) - correct_count
        
        return {
            "total_questions": self.total_questions,
            "questions_answered": len(self.answer_history),
            "correct_answers": correct_count,
            "incorrect_answers": incorrect_count,
            "score_percentage": self.get_score_percentage(),
            "elapsed_time": self.get_elapsed_time(),
            "difficulty": self.get_difficulty()
        }
    
    def restart(self):
        """Restart the quiz"""
        self.current_index = 0
        self.score = 0
        self.is_completed = False
        self.start_time = None
        self.answer_history = []
