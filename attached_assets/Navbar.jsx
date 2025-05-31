import { Link } from "react-router-dom";
import "../css/Navbar.css";
import { FaHome, FaBookOpen, FaQuestionCircle } from "react-icons/fa"; // icons
import { FaRegAddressCard } from "react-icons/fa"; // Thay vì FaQuestionCircle

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="logo glow">📘 Vocabulary App</div>
      <ul className="nav-links">
        <li>
          <Link to="/" className="nav-item">
            <FaHome className="icon" /> Home
          </Link>
        </li>
        <li>
          <Link to="/vocabulary" className="nav-item">
            <FaBookOpen className="icon" /> Vocabulary
          </Link>
        </li>
        <li>
          <Link to="/quiz" className="nav-item">
            <FaQuestionCircle className="icon" /> Quiz
          </Link>
        </li>
        <li>
       </li>
      </ul>
    </nav>
  );
};

export default Navbar;
