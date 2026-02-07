import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { AlertCircle, Activity, Users, FileText } from 'lucide-react';
import './Header.css';

const Header = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: Activity },
    { path: '/triage', label: 'New Triage', icon: AlertCircle },
    { path: '/resources', label: 'Resources', icon: Users },
  ];

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-brand">
          <AlertCircle className="header-icon" size={32} />
          <div>
            <h1 className="header-title">Emergency Crisis Triage</h1>
            <p className="header-subtitle">AI-Assisted Decision Support</p>
          </div>
        </div>

        <nav className="header-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${isActive ? 'active' : ''}`}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
};

export default Header;
