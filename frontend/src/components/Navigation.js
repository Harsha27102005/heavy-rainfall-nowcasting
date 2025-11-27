import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navigation = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Public Navigation
  if (!user) {
    return (
      <nav style={styles.nav} className="glass-panel">
        <div style={styles.container}>
          <Link to="/" style={styles.logo}>
            Rainfall<span style={{ color: 'var(--secondary-color)' }}>Nowcasting</span>
          </Link>

          <div style={styles.links}>
            <NavLink to="/login" current={location.pathname}>Login</NavLink>
            <NavLink to="/register" current={location.pathname}>Register</NavLink>
            <NavLink to="/guidelines" current={location.pathname}>Guidelines</NavLink>
            <NavLink to="/about" current={location.pathname}>About</NavLink>
          </div>
        </div>
      </nav>
    );
  }

  // Private Navigation
  return (
    <nav style={styles.nav} className="glass-panel">
      <div style={styles.container}>
        <Link to="/" style={styles.logo}>
          Rainfall<span style={{ color: 'var(--secondary-color)' }}>Nowcasting</span>
        </Link>

        <div style={styles.links}>
          <NavLink to="/" current={location.pathname}>Dashboard</NavLink>
          <NavLink to="/training" current={location.pathname}>Training</NavLink>
          <NavLink to="/settings" current={location.pathname}>Settings</NavLink>
          <NavLink to="/guidelines" current={location.pathname}>Safety</NavLink>
          <NavLink to="/report" current={location.pathname}>Report</NavLink>

          <div style={styles.userSection}>
            <span style={styles.username}>Hi, {user.username}</span>
            <button onClick={handleLogout} style={styles.logoutBtn}>
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

const NavLink = ({ to, current, children }) => {
  const isActive = current === to || (to === '/' && current === '/dashboard');
  return (
    <Link
      to={to}
      style={{
        ...styles.link,
        color: isActive ? 'var(--secondary-color)' : 'var(--text-color)',
        borderBottom: isActive ? '2px solid var(--secondary-color)' : '2px solid transparent'
      }}
    >
      {children}
    </Link>
  );
};

const styles = {
  nav: {
    position: 'fixed',
    top: '20px',
    left: '50%',
    transform: 'translateX(-50%)',
    width: '100%',
    maxWidth: '1260px',
    zIndex: 1000,
    padding: '0.8rem 2rem',
    display: 'flex',
    justifyContent: 'center',
  },
  container: {
    width: '100%',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  logo: {
    fontSize: '1.5rem',
    fontWeight: '700',
    color: 'var(--primary-color)',
    textDecoration: 'none',
  },
  links: {
    display: 'flex',
    gap: '2rem',
    alignItems: 'center',
  },
  link: {
    textDecoration: 'none',
    fontWeight: '500',
    padding: '0.5rem 0',
    transition: 'all 0.3s ease',
  },
  userSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    marginLeft: '1rem',
    paddingLeft: '1rem',
    borderLeft: '1px solid var(--glass-border)',
  },
  username: {
    fontSize: '0.9rem',
    color: 'var(--text-muted)',
  },
  logoutBtn: {
    background: 'rgba(255, 0, 80, 0.1)',
    border: '1px solid rgba(255, 0, 80, 0.3)',
    color: '#ff0050',
    padding: '0.4rem 1rem',
    borderRadius: '20px',
    cursor: 'pointer',
    fontSize: '0.85rem',
    transition: 'all 0.2s',
  }
};

export default Navigation;
