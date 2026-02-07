import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  AlertTriangle, 
  Clock, 
  CheckCircle, 
  Activity,
  TrendingUp,
  Users
} from 'lucide-react';
import { dashboardAPI, triageAPI } from '../services/api';
import RequestList from '../components/RequestList';
import './Dashboard.css';

const Dashboard = () => {
  // Fetch dashboard stats
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: dashboardAPI.getStats,
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  // Fetch recent requests
  const { data: requests, isLoading: requestsLoading } = useQuery({
    queryKey: ['requests'],
    queryFn: () => triageAPI.getRequests({ limit: 20 }),
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  if (statsLoading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Pending Requests',
      value: stats?.pending_requests || 0,
      icon: Clock,
      color: '#f59e0b',
      bgColor: '#fef3c7',
    },
    {
      title: 'Critical',
      value: stats?.critical_requests || 0,
      icon: AlertTriangle,
      color: '#dc2626',
      bgColor: '#fee2e2',
    },
    {
      title: 'High Urgency',
      value: stats?.high_urgency_requests || 0,
      icon: Activity,
      color: '#ea580c',
      bgColor: '#ffedd5',
    },
    {
      title: 'Completed Today',
      value: stats?.completed_requests || 0,
      icon: CheckCircle,
      color: '#16a34a',
      bgColor: '#dcfce7',
    },
    {
      title: 'Avg Triage Time',
      value: stats ? `${stats.average_triage_time_seconds.toFixed(1)}s` : '0s',
      icon: TrendingUp,
      color: '#3b82f6',
      bgColor: '#dbeafe',
    },
    {
      title: 'Resources Available',
      value: `${stats?.resources_available || 0}/${(stats?.resources_available || 0) + (stats?.resources_deployed || 0)}`,
      icon: Users,
      color: '#8b5cf6',
      bgColor: '#ede9fe',
    },
  ];

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Emergency Response Dashboard</h2>
        <p className="dashboard-subtitle">
          Real-time monitoring of emergency requests and resources
        </p>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div 
              key={index} 
              className="stat-card"
              style={{ borderLeft: `4px solid ${stat.color}` }}
            >
              <div className="stat-content">
                <div className="stat-header">
                  <span className="stat-title">{stat.title}</span>
                  <div 
                    className="stat-icon"
                    style={{ backgroundColor: stat.bgColor, color: stat.color }}
                  >
                    <Icon size={20} />
                  </div>
                </div>
                <div className="stat-value">{stat.value}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Key Performance Indicator */}
      {stats && stats.average_triage_time_seconds > 0 && (
        <div className="kpi-card">
          <div className="kpi-content">
            <TrendingUp size={24} className="kpi-icon" />
            <div>
              <h3>Time Savings Achievement</h3>
              <p>
                {stats.average_triage_time_seconds < 60 
                  ? `Excellent! Average triage time of ${stats.average_triage_time_seconds.toFixed(1)}s meets our 40% reduction goal.`
                  : `Current average: ${stats.average_triage_time_seconds.toFixed(1)}s. Working towards 40% reduction target.`
                }
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Recent Requests */}
      <div className="requests-section">
        <h3>Recent Emergency Requests</h3>
        {requestsLoading ? (
          <div className="spinner-small"></div>
        ) : (
          <RequestList requests={requests || []} />
        )}
      </div>
    </div>
  );
};

export default Dashboard;
