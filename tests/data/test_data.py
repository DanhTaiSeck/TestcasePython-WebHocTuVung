"""
Static test data for vocabulary testing
"""

# Sample vocabulary data for testing
SAMPLE_VOCABULARY = [
    {
        "word": "hello",
        "meaning": "xin chào",
        "difficulty": "easy",
        "category": "greeting"
    },
    {
        "word": "beautiful",
        "meaning": "đẹp",
        "difficulty": "medium",
        "category": "adjective"
    },
    {
        "word": "serendipity",
        "meaning": "may mắn bất ngờ",
        "difficulty": "hard",
        "category": "noun"
    },
    {
        "word": "study",
        "meaning": "học tập",
        "difficulty": "easy",
        "category": "verb"
    },
    {
        "word": "extraordinary",
        "meaning": "phi thường",
        "difficulty": "hard",
        "category": "adjective"
    }
]

# Quiz test data
QUIZ_TEST_DATA = [
    {
        "word": "cat",
        "meaning": "mèo",
        "difficulty": "easy"
    },
    {
        "word": "dog",
        "meaning": "chó",
        "difficulty": "easy"
    },
    {
        "word": "elephant",
        "meaning": "voi",
        "difficulty": "medium"
    },
    {
        "word": "beautiful",
        "meaning": "đẹp",
        "difficulty": "medium"
    },
    {
        "word": "serendipity",
        "meaning": "may mắn bất ngờ",
        "difficulty": "hard"
    }
]

# Invalid test data for error testing
INVALID_VOCABULARY_DATA = [
    {},  # Empty object
    {"word": "test"},  # Missing meaning
    {"meaning": "test"},  # Missing word
    {"word": "", "meaning": "test"},  # Empty word
    {"word": "test", "meaning": ""},  # Empty meaning
    {"word": None, "meaning": "test"},  # None word
    {"word": "test", "meaning": None}  # None meaning
]

# Edge case test data
EDGE_CASE_VOCABULARY = [
    {
        "word": "a",
        "meaning": "một"
    },
    {
        "word": "test-word",
        "meaning": "từ thử nghiệm"
    },
    {
        "word": "test_word",
        "meaning": "từ_thử_nghiệm"
    },
    {
        "word": "café",
        "meaning": "quán cà phê"
    },
    {
        "word": "naïve",
        "meaning": "ngây thơ"
    }
]

# Performance test data template
PERFORMANCE_TEST_TEMPLATE = {
    "word": "performance_test_{index}",
    "meaning": "kiểm tra hiệu suất {index}",
    "difficulty": "medium",
    "category": "test"
}

# API response schemas for validation
VOCABULARY_ITEM_SCHEMA = {
    "word": "string",
    "meaning": "string",
    "id": "integer"
}

VOCABULARY_LIST_SCHEMA = {
    "type": "array",
    "items": VOCABULARY_ITEM_SCHEMA
}

# Test configuration constants
TEST_CONSTANTS = {
    "MAX_WORD_LENGTH": 100,
    "MAX_MEANING_LENGTH": 500,
    "VALID_DIFFICULTIES": ["easy", "medium", "hard"],
    "VALID_CATEGORIES": ["noun", "verb", "adjective", "adverb", "phrase"],
    "DEFAULT_TIMEOUT": 30,
    "MAX_RETRIES": 3
}

# Security test payloads
XSS_PAYLOADS = [
    "<script>alert('xss')</script>",
    "<img src=x onerror=alert('xss')>",
    "javascript:alert('xss')",
    "<svg onload=alert('xss')>",
    "';alert('xss');//"
]

SQL_INJECTION_PAYLOADS = [
    "'; DROP TABLE vocabulary; --",
    "' OR '1'='1",
    "admin'--",
    "'; INSERT INTO vocabulary (word, meaning) VALUES ('hacked', 'pwned'); --",
    "' UNION SELECT * FROM vocabulary --"
]

# Unicode test data
UNICODE_TEST_DATA = [
    {"word": "café", "meaning": "quán cà phê"},
    {"word": "naïve", "meaning": "ngây thơ"},
    {"word": "résumé", "meaning": "sơ yếu lý lịch"},
    {"word": "piñata", "meaning": "búp bê giấy"},
    {"word": "jalapeño", "meaning": "ớt jalapeño"},
    {"word": "björk", "meaning": "tên riêng"},
    {"word": "москва", "meaning": "Moscow"},
    {"word": "東京", "meaning": "Tokyo"},
    {"word": "北京", "meaning": "Bắc Kinh"}
]

# Error messages for validation
ERROR_MESSAGES = {
    "MISSING_WORD": "Word is required",
    "MISSING_MEANING": "Meaning is required",
    "EMPTY_WORD": "Word cannot be empty",
    "EMPTY_MEANING": "Meaning cannot be empty",
    "WORD_TOO_LONG": "Word is too long",
    "MEANING_TOO_LONG": "Meaning is too long",
    "INVALID_DIFFICULTY": "Invalid difficulty level",
    "INVALID_CATEGORY": "Invalid category"
}
