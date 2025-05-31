import { Link } from "react-router-dom";
import "../css/Home.css";

const Home = () => {
  return (
    <div className="home-container">
      <div className="stars"></div>
      <div className="background-glow">
        <img src="./src/img/Chat2.png" alt="" />
      </div>
      <div className="home-content">
        <h1>🎓 Welcome to Vocabulary Galaxy</h1>
        <p>Boost your vocabulary while having fun 🚀</p>

        {/* Ảnh minh họa */}
        <div className="image-container" style={{ textAlign: 'center', marginTop: '20px', marginLeft: '-50px' }}>
  <img src="/src/img/ChatGPT.png" alt="Vocabulary Galaxy" style={{ maxWidth: '180px' }} />
</div>


        <div className="home-buttons">
          <Link to="/vocabulary" className="btn glow">
            Start Learning
          </Link>
          <Link to="/quiz" className="btn btn-outline">
            Take a Quiz
          </Link>
        </div>
        <p className="quote">“Learn a new word, open a new world.” 🌍</p>
      </div>
    </div>
  );
};

export default Home;