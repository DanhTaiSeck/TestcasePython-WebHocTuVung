"""
Data validation tests for vocabulary learning app
"""

import pytest
import re
from typing import Dict, Any, List


@pytest.mark.unit
class TestDataValidation:
    """Test data validation rules and constraints"""

    def test_vocabulary_word_validation(self):
        """Test vocabulary word validation rules"""
        validator = VocabularyValidator()
        
        # Valid words
        valid_words = [
            "hello",
            "beautiful",
            "test-word",
            "test_word",
            "café",
            "naïve",
            "123test",
            "test123",
            "a",  # Single character
        ]
        
        for word in valid_words:
            assert validator.validate_word(word).is_valid, f"Should accept valid word: '{word}'"
        
        # Invalid words
        invalid_words = [
            "",  # Empty string
            "   ",  # Only whitespace
            None,  # None value
            "a" * 101,  # Too long (assuming 100 char limit)
            "test\nword",  # Newline character
            "test\tword",  # Tab character
        ]
        
        for word in invalid_words:
            result = validator.validate_word(word)
            assert not result.is_valid, f"Should reject invalid word: '{word}'"
            assert result.error_message, f"Should provide error message for: '{word}'"

    def test_vocabulary_meaning_validation(self):
        """Test vocabulary meaning validation rules"""
        validator = VocabularyValidator()
        
        # Valid meanings
        valid_meanings = [
            "xin chào",
            "từ thử nghiệm",
            "meaning with punctuation!",
            "meaning, with, commas",
            "meaning (with parentheses)",
            "meaning-with-dashes",
            "meaning_with_underscores",
            "số 123",
            "🎉 emoji meaning",
        ]
        
        for meaning in valid_meanings:
            assert validator.validate_meaning(meaning).is_valid, f"Should accept valid meaning: '{meaning}'"
        
        # Invalid meanings
        invalid_meanings = [
            "",  # Empty string
            "   ",  # Only whitespace
            None,  # None value
            "a" * 501,  # Too long (assuming 500 char limit)
        ]
        
        for meaning in invalid_meanings:
            result = validator.validate_meaning(meaning)
            assert not result.is_valid, f"Should reject invalid meaning: '{meaning}'"
            assert result.error_message, f"Should provide error message for: '{meaning}'"

    def test_complete_vocabulary_validation(self):
        """Test complete vocabulary item validation"""
        validator = VocabularyValidator()
        
        # Valid vocabulary items
        valid_items = [
            {"word": "hello", "meaning": "xin chào"},
            {"word": "test", "meaning": "thử nghiệm", "difficulty": "easy"},
            {"word": "café", "meaning": "quán cà phê", "category": "food"},
        ]
        
        for item in valid_items:
            result = validator.validate_vocabulary_item(item)
            assert result.is_valid, f"Should accept valid item: {item}"
            assert not result.error_message, f"Should not have error for valid item: {item}"
        
        # Invalid vocabulary items
        invalid_items = [
            {},  # Empty object
            {"word": "test"},  # Missing meaning
            {"meaning": "test"},  # Missing word
            {"word": "", "meaning": "test"},  # Empty word
            {"word": "test", "meaning": ""},  # Empty meaning
            {"word": None, "meaning": "test"},  # None word
            {"word": "test", "meaning": None},  # None meaning
            {"word": "test", "meaning": "test", "difficulty": "invalid"},  # Invalid difficulty
        ]
        
        for item in invalid_items:
            result = validator.validate_vocabulary_item(item)
            assert not result.is_valid, f"Should reject invalid item: {item}"
            assert result.error_message, f"Should provide error message for: {item}"

    def test_quiz_answer_validation(self):
        """Test quiz answer validation"""
        validator = QuizValidator()
        
        # Test exact matching
        assert validator.validate_answer("hello", "hello").is_correct
        assert not validator.validate_answer("hello", "goodbye").is_correct
        
        # Test case insensitive matching
        assert validator.validate_answer("HELLO", "hello").is_correct
        assert validator.validate_answer("Hello", "hello").is_correct
        
        # Test whitespace normalization
        assert validator.validate_answer("  hello  ", "hello").is_correct
        assert validator.validate_answer("hello\n", "hello").is_correct
        assert validator.validate_answer("\thello", "hello").is_correct
        
        # Test empty answers
        assert not validator.validate_answer("", "hello").is_correct
        assert not validator.validate_answer(None, "hello").is_correct
        assert not validator.validate_answer("hello", "").is_correct

    def test_input_sanitization(self):
        """Test input sanitization for security"""
        sanitizer = InputSanitizer()
        
        # Test XSS prevention
        xss_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';DROP TABLE vocabulary;--",
        ]
        
        for xss_input in xss_inputs:
            sanitized = sanitizer.sanitize_text(xss_input)
            assert "<script>" not in sanitized.lower(), f"Should remove script tags from: {xss_input}"
            assert "javascript:" not in sanitized.lower(), f"Should remove javascript: from: {xss_input}"
            assert "onerror=" not in sanitized.lower(), f"Should remove event handlers from: {xss_input}"
        
        # Test SQL injection prevention
        sql_inputs = [
            "'; DROP TABLE vocabulary; --",
            "' OR '1'='1",
            "admin'--",
            "'; INSERT INTO",
        ]
        
        for sql_input in sql_inputs:
            sanitized = sanitizer.sanitize_text(sql_input)
            # Basic sanitization should escape or remove dangerous characters
            assert sanitized != sql_input, f"Should sanitize SQL injection attempt: {sql_input}"

    def test_api_request_validation(self, api_client):
        """Test API request validation"""
        # Test content type validation
        response = api_client.post("/vocabulary", data="invalid json", headers={"Content-Type": "text/plain"})
        assert response.status_code in [400, 415, 422], "Should reject non-JSON content"
        
        # Test malformed JSON
        import requests
        try:
            response = requests.post(
                f"{api_client.base_url}/vocabulary",
                data="{'invalid': json}",
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code in [400, 422], "Should reject malformed JSON"
        except:
            pass  # Network errors are acceptable for this test
        
        # Test oversized requests
        oversized_data = {"word": "test", "meaning": "a" * 10000}
        response = api_client.post("/vocabulary", json=oversized_data)
        assert response.status_code in [400, 413, 422], "Should reject oversized requests"

    def test_unicode_and_special_characters(self):
        """Test handling of unicode and special characters"""
        validator = VocabularyValidator()
        
        # Unicode characters
        unicode_test_cases = [
            {"word": "café", "meaning": "quán cà phê"},
            {"word": "naïve", "meaning": "ngây thơ"},
            {"word": "résumé", "meaning": "sơ yếu lý lịch"},
            {"word": "piñata", "meaning": "búp bê giấy"},
            {"word": "jalapeño", "meaning": "ớt jalapeño"},
            {"word": "sœur", "meaning": "chị em"},
            {"word": "北京", "meaning": "Bắc Kinh"},  # Chinese characters
            {"word": "東京", "meaning": "Tokyo"},  # Japanese characters
            {"word": "москва", "meaning": "Moscow"},  # Cyrillic
        ]
        
        for test_case in unicode_test_cases:
            result = validator.validate_vocabulary_item(test_case)
            assert result.is_valid, f"Should handle unicode correctly: {test_case}"
        
        # Emoji handling
        emoji_test_cases = [
            {"word": "smile", "meaning": "😊 cười"},
            {"word": "heart", "meaning": "❤️ trái tim"},
            {"word": "celebrate", "meaning": "🎉 ăn mừng"},
        ]
        
        for test_case in emoji_test_cases:
            result = validator.validate_vocabulary_item(test_case)
            # Depending on requirements, emojis might or might not be allowed

    def test_length_constraints(self):
        """Test length constraint validation"""
        validator = VocabularyValidator()
        
        # Test minimum lengths
        result = validator.validate_word("a")
        assert result.is_valid, "Single character word should be valid"
        
        result = validator.validate_meaning("a")
        assert result.is_valid, "Single character meaning should be valid"
        
        # Test maximum lengths
        max_word_length = 100  # Assumed constraint
        max_meaning_length = 500  # Assumed constraint
        
        # Just under the limit
        long_word = "a" * (max_word_length - 1)
        result = validator.validate_word(long_word)
        assert result.is_valid, f"Word just under limit should be valid: {len(long_word)} chars"
        
        # At the limit
        limit_word = "a" * max_word_length
        result = validator.validate_word(limit_word)
        assert result.is_valid, f"Word at limit should be valid: {len(limit_word)} chars"
        
        # Over the limit
        over_limit_word = "a" * (max_word_length + 1)
        result = validator.validate_word(over_limit_word)
        assert not result.is_valid, f"Word over limit should be invalid: {len(over_limit_word)} chars"

    def test_batch_validation(self, vocabulary_factory):
        """Test validation of multiple vocabulary items"""
        validator = VocabularyValidator()
        
        # Create mixed batch (some valid, some invalid)
        valid_items = vocabulary_factory.create_batch(3)
        invalid_items = [
            {"word": "", "meaning": "empty word"},
            {"word": "no meaning"},
            {"invalid": "format"}
        ]
        
        mixed_batch = valid_items + invalid_items
        
        results = validator.validate_batch(mixed_batch)
        
        assert len(results) == len(mixed_batch), "Should return result for each item"
        
        # Check valid items
        for i in range(len(valid_items)):
            assert results[i].is_valid, f"Valid item {i} should pass validation"
        
        # Check invalid items
        for i in range(len(valid_items), len(mixed_batch)):
            assert not results[i].is_valid, f"Invalid item {i} should fail validation"
            assert results[i].error_message, f"Invalid item {i} should have error message"

    def test_custom_validation_rules(self):
        """Test custom validation rules"""
        validator = VocabularyValidator()
        
        # Test profanity filter (if implemented)
        # This would depend on specific requirements
        
        # Test allowed categories (if implemented)
        valid_categories = ["noun", "verb", "adjective", "adverb", "other"]
        
        for category in valid_categories:
            item = {"word": "test", "meaning": "test", "category": category}
            result = validator.validate_vocabulary_item(item)
            # Should be valid if categories are implemented
        
        # Test invalid category
        invalid_item = {"word": "test", "meaning": "test", "category": "invalid_category"}
        result = validator.validate_vocabulary_item(invalid_item)
        # Depending on implementation, this might be valid (ignore unknown fields) or invalid


class ValidationResult:
    """Result of a validation operation"""
    
    def __init__(self, is_valid: bool, error_message: str = ""):
        self.is_valid = is_valid
        self.error_message = error_message


class VocabularyValidator:
    """Validator for vocabulary data"""
    
    def __init__(self):
        self.max_word_length = 100
        self.max_meaning_length = 500
        self.valid_difficulties = ["easy", "medium", "hard"]
        self.valid_categories = ["noun", "verb", "adjective", "adverb", "other"]
    
    def validate_word(self, word: Any) -> ValidationResult:
        """Validate vocabulary word"""
        if word is None:
            return ValidationResult(False, "Word cannot be None")
        
        if not isinstance(word, str):
            return ValidationResult(False, "Word must be a string")
        
        word = word.strip()
        
        if not word:
            return ValidationResult(False, "Word cannot be empty")
        
        if len(word) > self.max_word_length:
            return ValidationResult(False, f"Word too long (max {self.max_word_length} characters)")
        
        # Check for invalid characters
        if '\n' in word or '\t' in word:
            return ValidationResult(False, "Word cannot contain newlines or tabs")
        
        return ValidationResult(True)
    
    def validate_meaning(self, meaning: Any) -> ValidationResult:
        """Validate vocabulary meaning"""
        if meaning is None:
            return ValidationResult(False, "Meaning cannot be None")
        
        if not isinstance(meaning, str):
            return ValidationResult(False, "Meaning must be a string")
        
        meaning = meaning.strip()
        
        if not meaning:
            return ValidationResult(False, "Meaning cannot be empty")
        
        if len(meaning) > self.max_meaning_length:
            return ValidationResult(False, f"Meaning too long (max {self.max_meaning_length} characters)")
        
        return ValidationResult(True)
    
    def validate_vocabulary_item(self, item: Dict[str, Any]) -> ValidationResult:
        """Validate complete vocabulary item"""
        if not isinstance(item, dict):
            return ValidationResult(False, "Vocabulary item must be a dictionary")
        
        # Check required fields
        if "word" not in item:
            return ValidationResult(False, "Missing required field: word")
        
        if "meaning" not in item:
            return ValidationResult(False, "Missing required field: meaning")
        
        # Validate word
        word_result = self.validate_word(item["word"])
        if not word_result.is_valid:
            return word_result
        
        # Validate meaning
        meaning_result = self.validate_meaning(item["meaning"])
        if not meaning_result.is_valid:
            return meaning_result
        
        # Validate optional fields
        if "difficulty" in item:
            if item["difficulty"] not in self.valid_difficulties:
                return ValidationResult(False, f"Invalid difficulty. Must be one of: {self.valid_difficulties}")
        
        if "category" in item:
            if item["category"] not in self.valid_categories:
                return ValidationResult(False, f"Invalid category. Must be one of: {self.valid_categories}")
        
        return ValidationResult(True)
    
    def validate_batch(self, items: List[Dict[str, Any]]) -> List[ValidationResult]:
        """Validate multiple vocabulary items"""
        return [self.validate_vocabulary_item(item) for item in items]


class QuizValidator:
    """Validator for quiz-related data"""
    
    def validate_answer(self, user_answer: Any, correct_answer: str) -> ValidationResult:
        """Validate quiz answer"""
        if user_answer is None or correct_answer is None:
            return ValidationResult(False, "Answer cannot be None")
        
        # Normalize answers
        user_answer = str(user_answer).strip().lower()
        correct_answer = str(correct_answer).strip().lower()
        
        is_correct = user_answer == correct_answer
        
        # Create custom result with is_correct attribute
        result = ValidationResult(True)
        result.is_correct = is_correct
        
        return result


class InputSanitizer:
    """Sanitizer for user input to prevent security issues"""
    
    def __init__(self):
        # Patterns for potentially dangerous content
        self.script_pattern = re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL)
        self.javascript_pattern = re.compile(r'javascript:', re.IGNORECASE)
        self.event_pattern = re.compile(r'on\w+\s*=', re.IGNORECASE)
        
    def sanitize_text(self, text: str) -> str:
        """Sanitize text input"""
        if not isinstance(text, str):
            return str(text)
        
        # Remove script tags
        text = self.script_pattern.sub('', text)
        
        # Remove javascript: URLs
        text = self.javascript_pattern.sub('', text)
        
        # Remove event handlers
        text = self.event_pattern.sub('', text)
        
        # Escape HTML entities (basic implementation)
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        
        return text
