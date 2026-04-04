import { NavLink } from 'react-router-dom';
import './Header.css';

export default function Header() {
  return (
    <header className="header">
      <div className="logo">Loan<span>Guard</span></div>
      <nav className="nav">
        <NavLink to="/"          className={({isActive}) => isActive ? 'nav-link active' : 'nav-link'}>Predict</NavLink>
        <NavLink to="/dashboard" className={({isActive}) => isActive ? 'nav-link active' : 'nav-link'}>Dashboard</NavLink>
      </nav>
      <div className="api-status">
        <span className="pulse-dot" />
        API live
      </div>
    </header>
  );
}