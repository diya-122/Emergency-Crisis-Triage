import React from 'react';
import { Link } from 'react-router-dom';
import { formatDistance } from 'date-fns';
import { Clock, MapPin, AlertTriangle, Users } from 'lucide-react';
import './RequestList.css';

const RequestList = ({ requests }) => {
  if (!requests || requests.length === 0) {
    return (
      <div className="empty-state">
        <AlertTriangle size={48} color="#9ca3af" />
        <p>No emergency requests found</p>
      </div>
    );
  }

  const getUrgencyClass = (level) => {
    const classes = {
      critical: 'urgency-badge urgency-critical',
      high: 'urgency-badge urgency-high',
      medium: 'urgency-badge urgency-medium',
      low: 'urgency-badge urgency-low',
    };
    return classes[level] || 'urgency-badge';
  };

  const getStatusClass = (status) => {
    const classes = {
      pending: 'status-badge status-pending',
      processing: 'status-badge status-processing',
      dispatched: 'status-badge status-dispatched',
      completed: 'status-badge status-completed',
      cancelled: 'status-badge status-cancelled',
    };
    return classes[status] || 'status-badge';
  };

  return (
    <div className="request-list">
      {requests.map((request) => (
        <Link
          key={request.request_id}
          to={`/requests/${request.request_id}`}
          className="request-card"
        >
          <div className="request-header">
            <div className="request-badges">
              <span className={getUrgencyClass(request.extracted_info?.urgency_level)}>
                {request.extracted_info?.urgency_level?.toUpperCase() || 'UNKNOWN'}
              </span>
              <span className={getStatusClass(request.status)}>
                {request.status}
              </span>
            </div>
            <div className="request-time">
              <Clock size={14} />
              <span>
                {formatDistance(new Date(request.received_at), new Date(), {
                  addSuffix: true,
                })}
              </span>
            </div>
          </div>

          <div className="request-message">
            {request.original_message.substring(0, 150)}
            {request.original_message.length > 150 && '...'}
          </div>

          <div className="request-footer">
            {request.extracted_info?.location && (
              <div className="request-info">
                <MapPin size={14} />
                <span>
                  {request.extracted_info.location.address || 
                   request.extracted_info.location.raw_text}
                </span>
              </div>
            )}
            {request.extracted_info?.people_affected && (
              <div className="request-info">
                <Users size={14} />
                <span>{request.extracted_info.people_affected} people</span>
              </div>
            )}
          </div>

          {request.extracted_info?.urgency_score !== undefined && (
            <div className="request-score">
              <div className="score-bar-container">
                <div
                  className="score-bar"
                  style={{
                    width: `${request.extracted_info.urgency_score * 100}%`,
                    backgroundColor: 
                      request.extracted_info.urgency_score > 0.75 ? '#dc2626' :
                      request.extracted_info.urgency_score > 0.5 ? '#ea580c' :
                      request.extracted_info.urgency_score > 0.25 ? '#ca8a04' :
                      '#16a34a'
                  }}
                />
              </div>
              <span className="score-text">
                Urgency Score: {(request.extracted_info.urgency_score * 100).toFixed(0)}%
              </span>
            </div>
          )}
        </Link>
      ))}
    </div>
  );
};

export default RequestList;
