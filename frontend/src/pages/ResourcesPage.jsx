import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Users, Activity, MapPin, Package } from 'lucide-react';
import { resourcesAPI } from '../services/api';
import './ResourcesPage.css';

const ResourcesPage = () => {
  const { data: resources, isLoading } = useQuery({
    queryKey: ['resources'],
    queryFn: () => resourcesAPI.getResources(),
    refetchInterval: 10000,
  });

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading resources...</p>
      </div>
    );
  }

  const getStatusClass = (status) => {
    const classes = {
      active: 'status-active',
      deployed: 'status-deployed',
      inactive: 'status-inactive',
    };
    return classes[status] || '';
  };

  const getCapacityColor = (current, total) => {
    const ratio = current / total;
    if (ratio > 0.7) return '#10b981';
    if (ratio > 0.3) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="resources-page">
      <div className="page-header">
        <div className="header-icon-wrapper">
          <Users size={32} />
        </div>
        <div>
          <h2>Available Resources</h2>
          <p className="page-description">
            Monitor and manage emergency response resources
          </p>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="resource-stats">
        <div className="stat-item">
          <Activity size={20} />
          <div>
            <div className="stat-value">
              {resources?.filter(r => r.status === 'active').length || 0}
            </div>
            <div className="stat-label">Active</div>
          </div>
        </div>
        <div className="stat-item">
          <Package size={20} />
          <div>
            <div className="stat-value">
              {resources?.filter(r => r.status === 'deployed').length || 0}
            </div>
            <div className="stat-label">Deployed</div>
          </div>
        </div>
        <div className="stat-item">
          <Users size={20} />
          <div>
            <div className="stat-value">
              {resources?.reduce((sum, r) => sum + r.current_availability, 0) || 0}
            </div>
            <div className="stat-label">Total Capacity</div>
          </div>
        </div>
      </div>

      {/* Resources Grid */}
      <div className="resources-grid">
        {resources && resources.length > 0 ? (
          resources.map((resource) => (
            <div key={resource.resource_id} className="resource-item">
              <div className="resource-item-header">
                <h3>{resource.name}</h3>
                <span className={`status-badge ${getStatusClass(resource.status)}`}>
                  {resource.status}
                </span>
              </div>

              <div className="resource-type-badge">
                {resource.resource_type.replace('_', ' ')}
              </div>

              <p className="resource-description">{resource.description}</p>

              <div className="resource-location">
                <MapPin size={14} />
                <span>{resource.location.address}</span>
              </div>

              <div className="resource-capacity">
                <div className="capacity-header">
                  <span>Capacity</span>
                  <span>
                    {resource.current_availability} / {resource.capacity}
                  </span>
                </div>
                <div className="capacity-bar">
                  <div
                    className="capacity-fill"
                    style={{
                      width: `${(resource.current_availability / resource.capacity) * 100}%`,
                      backgroundColor: getCapacityColor(
                        resource.current_availability,
                        resource.capacity
                      ),
                    }}
                  />
                </div>
              </div>

              {resource.capabilities && resource.capabilities.length > 0 && (
                <div className="resource-capabilities">
                  <strong>Capabilities:</strong>
                  <div className="capabilities-tags">
                    {resource.capabilities.map((cap, idx) => (
                      <span key={idx} className="capability-tag">
                        {cap.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="resource-footer">
                <span className="response-time">
                  ~{resource.estimated_response_time_minutes} min response
                </span>
              </div>
            </div>
          ))
        ) : (
          <div className="empty-state">
            <Users size={48} />
            <p>No resources available</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResourcesPage;
