import React, { useState, useEffect } from "react";
import axios from "axios";
import "../css/Vocabulary.css";
import { useNavigate } from "react-router-dom";

const API_URL = "http://localhost:3000/api/vocabulary";

const Vocabulary = () => {
  const [vocabularyList, setVocabularyList] = useState([]);
  const [inputText, setInputText] = useState("");
  const [editId, setEditId] = useState(null); // ID từ đang sửa

  // 📌 Lấy danh sách từ vựng từ API khi component mount
  useEffect(() => {
    fetchVocabulary();
  }, []);

  const fetchVocabulary = async () => {
    try {
      const response = await axios.get(API_URL);
      setVocabularyList(response.data);
    } catch (error) {
      console.error("Lỗi tải từ vựng:", error);
    }
  };

  // 📌 Hàm kiểm tra định dạng & tách từ vựng nhiều dòng
  const parseVocabulary = (text) => {
    const regex = /^(.+?)\s*[:-]\s*(.+)$/;
    return text
      .split("\n")
      .map((line) => line.match(regex))
      .filter(Boolean)
      .map((match) => ({ word: match[1].trim(), meaning: match[2].trim() }));
  };

  // 📌 Thêm nhiều từ mới
  const handleAddWords = async () => {
    const parsedWords = parseVocabulary(inputText);
    if (parsedWords.length > 0) {
      try {
        await Promise.all(
          parsedWords.map(async (item) => {
            await axios.post(API_URL, item);
          })
        );
        fetchVocabulary(); // Load lại danh sách từ vựng
        setInputText("");
      } catch (error) {
        console.error("Lỗi thêm từ:", error);
      }
    } else {
      alert("Hãy nhập theo định dạng: 'word: meaning' hoặc 'word - meaning'");
    }
  };

  // 📌 Chỉnh sửa từ vựng
  const handleEditWord = (id) => {
    const item = vocabularyList.find((word) => word.id === id);
    if (item) {
      setInputText(`${item.word}: ${item.meaning}`);
      setEditId(id);
    }
  };

  // 📌 Cập nhật từ vựng
  const handleUpdateWord = async () => {
    const parsedWords = parseVocabulary(inputText);
    if (parsedWords.length === 1 && editId !== null) {
      try {
        await axios.put(`${API_URL}/${editId}`, parsedWords[0]);
        fetchVocabulary();
        setInputText("");
        setEditId(null);
      } catch (error) {
        console.error("Lỗi cập nhật từ:", error);
      }
    } else {
      alert("Hãy nhập đúng định dạng và chỉ 1 dòng khi chỉnh sửa!");
    }
  };

  // 📌 Xóa từ vựng
  const handleDeleteWord = async (id) => {
    try {
      await axios.delete(`${API_URL}/${id}`);
      fetchVocabulary();
    } catch (error) {
      console.error("Lỗi xóa từ:", error);
    }
  };

  return (
    <div className="vocabulary-body">
      <div className="vocabulary-container">
        <h1 className="title">Vocabulary List</h1>

        {/* Ô nhập từ mới */}
        <div className="input-container">
          <textarea
            placeholder="Nhập từ vựng (vd: sun: mặt trời) - có thể nhập nhiều dòng"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            rows={4}
          />
          {editId === null ? (
            <button onClick={handleAddWords}>Thêm từ</button>
          ) : (
            <button onClick={handleUpdateWord}>Cập nhật</button>
          )}
        </div>

        {/* Danh sách từ vựng */}
        <ul className="word-list">
          {vocabularyList.map((item) => (
            <li key={item.id} className="word-item">
              <span className="word">{item.word}</span>
              <span className="meaning"> {item.meaning}</span>
              <button className="edit-btn" onClick={() => handleEditWord(item.id)}>
                Sửa
              </button>
              <button className="delete-btn" onClick={() => handleDeleteWord(item.id)}>
                Xóa
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default Vocabulary;
