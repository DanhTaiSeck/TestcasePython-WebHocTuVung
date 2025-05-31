"""
Factory for generating test vocabulary data
"""

from faker import Faker
from typing import Dict, List, Any
import random


class VocabularyFactory:
    """Factory for creating vocabulary test data"""
    
    def __init__(self, locale: str = 'en_US'):
        self.fake = Faker([locale, 'vi_VN'])  # English and Vietnamese
        
        # Predefined vocabulary for consistency
        self.english_words = [
            "hello", "goodbye", "please", "thank", "sorry",
            "beautiful", "ugly", "big", "small", "fast",
            "slow", "happy", "sad", "good", "bad",
            "house", "car", "book", "table", "chair",
            "water", "food", "money", "time", "love",
            "family", "friend", "work", "school", "study",
            "computer", "phone", "internet", "music", "movie",
            "cat", "dog", "bird", "fish", "tree",
            "sun", "moon", "star", "sky", "earth",
            "red", "blue", "green", "yellow", "black"
        ]
        
        self.vietnamese_meanings = [
            "xin chào", "tạm biệt", "xin lỗi", "cảm ơn", "xin lỗi",
            "đẹp", "xấu", "to", "nhỏ", "nhanh",
            "chậm", "vui", "buồn", "tốt", "xấu",
            "nhà", "xe hơi", "sách", "bàn", "ghế",
            "nước", "thức ăn", "tiền", "thời gian", "tình yêu",
            "gia đình", "bạn", "công việc", "trường học", "học tập",
            "máy tính", "điện thoại", "internet", "âm nhạc", "phim",
            "mèo", "chó", "chim", "cá", "cây",
            "mặt trời", "mặt trăng", "ngôi sao", "bầu trời", "trái đất",
            "đỏ", "xanh dương", "xanh lá", "vàng", "đen"
        ]
        
        self.difficulties = ["easy", "medium", "hard"]
        self.categories = ["noun", "verb", "adjective", "adverb", "phrase"]
        
    def create(self, **kwargs) -> Dict[str, Any]:
        """Create a single vocabulary item"""
        # Use predefined words for consistency, or generate random ones
        if random.choice([True, False]) and self.english_words:
            index = random.randint(0, min(len(self.english_words), len(self.vietnamese_meanings)) - 1)
            word = self.english_words[index]
            meaning = self.vietnamese_meanings[index]
        else:
            word = self.fake.word()
            meaning = self._generate_vietnamese_meaning()
        
        vocabulary = {
            "word": word,
            "meaning": meaning,
            "difficulty": random.choice(self.difficulties),
            "category": random.choice(self.categories),
            "created_at": self.fake.date_time_this_year().isoformat(),
            "example": self._generate_example_sentence(word)
        }
        
        # Override with any provided kwargs
        vocabulary.update(kwargs)
        
        return vocabulary
    
    def create_batch(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """Create multiple vocabulary items"""
        return [self.create(**kwargs) for _ in range(count)]
    
    def create_minimal(self, **kwargs) -> Dict[str, Any]:
        """Create vocabulary item with only required fields"""
        if random.choice([True, False]) and self.english_words:
            index = random.randint(0, min(len(self.english_words), len(self.vietnamese_meanings)) - 1)
            word = self.english_words[index]
            meaning = self.vietnamese_meanings[index]
        else:
            word = self.fake.word()
            meaning = self._generate_vietnamese_meaning()
        
        vocabulary = {
            "word": word,
            "meaning": meaning
        }
        
        vocabulary.update(kwargs)
        return vocabulary
    
    def create_with_difficulty(self, difficulty: str, count: int = 1) -> List[Dict[str, Any]]:
        """Create vocabulary items with specific difficulty"""
        return self.create_batch(count, difficulty=difficulty)
    
    def create_invalid(self, invalid_type: str = "missing_field") -> Dict[str, Any]:
        """Create invalid vocabulary data for testing"""
        if invalid_type == "missing_field":
            return {"word": self.fake.word()}  # Missing meaning
        elif invalid_type == "empty_field":
            return {"word": "", "meaning": self.fake.word()}
        elif invalid_type == "wrong_type":
            return {"word": 123, "meaning": self.fake.word()}
        elif invalid_type == "too_long":
            return {"word": "a" * 200, "meaning": self.fake.word()}
        else:
            return {}
    
    def create_quiz_data(self, count: int = 10) -> List[Dict[str, Any]]:
        """Create vocabulary data specifically for quiz testing"""
        quiz_words = []
        
        # Ensure we have a mix of difficulties
        easy_count = count // 3
        medium_count = count // 3
        hard_count = count - easy_count - medium_count
        
        quiz_words.extend(self.create_with_difficulty("easy", easy_count))
        quiz_words.extend(self.create_with_difficulty("medium", medium_count))
        quiz_words.extend(self.create_with_difficulty("hard", hard_count))
        
        return quiz_words
    
    def create_performance_dataset(self, count: int = 1000) -> List[Dict[str, Any]]:
        """Create large dataset for performance testing"""
        # For performance testing, create simpler data to speed up generation
        dataset = []
        
        for i in range(count):
            word = f"word_{i:04d}"
            meaning = f"nghĩa_{i:04d}"
            
            dataset.append({
                "word": word,
                "meaning": meaning,
                "difficulty": random.choice(self.difficulties),
                "category": random.choice(self.categories)
            })
        
        return dataset
    
    def create_unicode_test_data(self) -> List[Dict[str, Any]]:
        """Create vocabulary data with unicode characters for testing"""
        unicode_test_cases = [
            {"word": "café", "meaning": "quán cà phê"},
            {"word": "naïve", "meaning": "ngây thơ"},
            {"word": "résumé", "meaning": "sơ yếu lý lịch"},
            {"word": "piñata", "meaning": "búp bê giấy"},
            {"word": "jalapeño", "meaning": "ớt jalapeño"},
            {"word": "façade", "meaning": "mặt tiền"},
            {"word": "björk", "meaning": "tên riêng"},
            {"word": "москва", "meaning": "Moscow"},
            {"word": "東京", "meaning": "Tokyo"},
            {"word": "北京", "meaning": "Bắc Kinh"},
        ]
        
        return unicode_test_cases
    
    def create_edge_case_data(self) -> List[Dict[str, Any]]:
        """Create edge case data for testing"""
        edge_cases = [
            # Single character
            {"word": "a", "meaning": "chữ a"},
            {"word": "I", "meaning": "tôi"},
            
            # With numbers
            {"word": "test123", "meaning": "thử nghiệm 123"},
            {"word": "123test", "meaning": "123 thử nghiệm"},
            
            # With special characters
            {"word": "test-word", "meaning": "từ thử nghiệm"},
            {"word": "test_word", "meaning": "từ_thử_nghiệm"},
            {"word": "test.word", "meaning": "từ.thử.nghiệm"},
            
            # Long words (within limits)
            {"word": "a" * 50, "meaning": "từ dài"},
            {"word": "test", "meaning": "nghĩa rất dài " * 10},
            
            # With punctuation
            {"word": "don't", "meaning": "không"},
            {"word": "it's", "meaning": "nó là"},
            {"word": "can't", "meaning": "không thể"},
        ]
        
        return edge_cases
    
    def _generate_vietnamese_meaning(self) -> str:
        """Generate a Vietnamese meaning"""
        vietnamese_words = [
            "là", "có", "của", "một", "không", "được", "đã", "sẽ", "này", "đó",
            "tôi", "bạn", "chúng", "họ", "người", "thời gian", "nơi", "việc",
            "tốt", "xấu", "lớn", "nhỏ", "mới", "cũ", "đẹp", "xấu xí",
            "yêu", "thích", "ghét", "muốn", "cần", "phải", "nên", "có thể"
        ]
        
        # Generate 1-3 word meaning
        word_count = random.randint(1, 3)
        meaning_words = random.sample(vietnamese_words, word_count)
        return " ".join(meaning_words)
    
    def _generate_example_sentence(self, word: str) -> str:
        """Generate an example sentence using the word"""
        sentence_templates = [
            f"I use {word} every day.",
            f"The {word} is very important.",
            f"Can you give me a {word}?",
            f"This {word} belongs to me.",
            f"I love this {word}.",
        ]
        
        return random.choice(sentence_templates)
    
    def reset_seed(self, seed: int = 42):
        """Reset random seed for reproducible test data"""
        self.fake.seed_instance(seed)
        random.seed(seed)
