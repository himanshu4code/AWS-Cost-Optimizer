import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function Navigation() {
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navigation">
      <div className="nav-brand" onClick={() => navigate('/dashboard')}>
        <span className="nav-logo">💰</span>
        <div className="nav-branding">
          <p className="nav-eyebrow">AWS Cost Optimizer</p>
          <h2 className="nav-title">Optimizer</h2>
        </div>
      </div>

      <ul className="nav-links">
          <li>
            <button 
              className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}
              onClick={() => navigate('/dashboard')}
            >
              Dashboard
            </button>
          </li>
          <li>
            <button 
              className={`nav-link ${isActive('/configuration') ? 'active' : ''}`}
              onClick={() => navigate('/configuration')}
            >
              Configuration
            </button>
          </li>
          <li>
            <button 
              className={`nav-link ${isActive('/reports') ? 'active' : ''}`}
              onClick={() => navigate('/reports')}
            >
              Reports
            </button>
          </li>
      </ul>

    </nav>
  );
}
