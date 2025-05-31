import { useState, useEffect } from "react";
import axios from "axios";
import "../css/QuizPage.css"; // Import CSS riêng
import { Link } from "react-router-dom";


const VocabularyQuiz = () => {
  const [vocabularyList, setVocabularyList] = useState([]);
  const [index, setIndex] = useState(0);
  const [userAnswer, setUserAnswer] = useState("");
  const [score, setScore] = useState(0);
  const [showResult, setShowResult] = useState(false);
  const [quizStarted, setQuizStarted] = useState(false);

  // Lấy danh sách từ vựng từ API khi component load
  useEffect(() => {
    const fetchVocabulary = async () => {
      try {
        const response = await axios.get("http://localhost:3000/api/vocabulary"); // Đảm bảo API của bạn đúng URL
        setVocabularyList(response.data);
      } catch (error) {
        console.error("Lỗi tải từ vựng:", error);
      }
    };

    fetchVocabulary();
  }, []);

  const handleSubmit = () => {
    if (userAnswer.trim().toLowerCase() === vocabularyList[index].meaning.toLowerCase()) {
      setScore(score + 1);
    }
    if (index < vocabularyList.length - 1) {
      setIndex(index + 1);
      setUserAnswer("");
    } else {
      setShowResult(true);
    }
  };

  const handleRestart = () => {
    setIndex(0);
    setScore(0);
    setShowResult(false);
    setUserAnswer("");
    setQuizStarted(false);
  };

  // Hàm xử lý sự kiện khi nhấn Enter trong input
  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSubmit(); // Khi nhấn Enter, gọi handleSubmit
    }
  };

  return (
    <div className="quiz-body">
      <div className="quiz-container">
        {!quizStarted ? (
          <button onClick={() => setQuizStarted(true)} className="start-btn">
            Bắt đầu kiểm tra 🚀
          </button>
        ) : !showResult ? (
          <>
            <div className="quiz-test">
              <h2 className="word">{vocabularyList[index]?.word}</h2>
              <input
                type="text"
                placeholder="Nhập nghĩa tiếng Việt..."
                value={userAnswer}
                onChange={(e) => setUserAnswer(e.target.value)}
                className="input-box"
                onKeyDown={handleKeyDown} // Xử lý sự kiện khi nhấn phím
              />
              <button onClick={handleSubmit} className="check-btn">
                Kiểm tra
              </button>
            </div>
          </>
        ) : (
          <div>
            <h3 className="score-text">
              🎉 Bạn đã hoàn thành! Điểm của bạn: {score}/{vocabularyList.length}
            </h3>
            <button onClick={handleRestart} className="restart-btn">
              Thử lại 🔄
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default VocabularyQuiz;
