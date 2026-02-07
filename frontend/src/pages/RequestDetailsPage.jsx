import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  AlertCircle, Clock, MapPin, Users, CheckCircle,
  XCircle, FileText, TrendingUp, Navigation
} from 'lucide-react';
import { triageAPI } from '../services/api';
import './RequestDetailsPage.css';

const RequestDetailsPage = () => {
  const { requestId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [selectedResourceId, setSelectedResourceId] = useState('');
  const [notes, setNotes] = useState('');
  const [dispatcherId] = useState('dispatcher-001'); // In production, get from auth

  const { data: request, isLoading } = useQuery({
    queryKey: ['request', requestId],
    queryFn: () => triageAPI.getRequest(requestId),
  });

  const confirmMutation = useMutation({
    mutationFn: triageAPI.confirmDispatch,
    onSuccess: () => {
      queryClient.invalidateQueries(['request', requestId]);
      queryClient.invalidateQueries(['requests']);
      alert('Dispatch confirmed successfully!');
    },
  });

  const handleConfirm = () => {
    if (!selectedResourceId) {
      alert('Please select a resource to dispatch');
      return;
    }

    const confirmation = {
      request_id: requestId,
      confirmed: true,
      selected_resource_id: selectedResourceId,
      dispatcher_notes: notes || null,
      dispatcher_id: dispatcherId,
      override_reason: null,
    };

    if (window.confirm('Confirm dispatch of selected resource?')) {
      confirmMutation.mutate(confirmation);
    }
  };

  const handleCancel = () => {
    if (window.confirm('Cancel this request?')) {
      confirmMutation.mutate({
        request_id: requestId,
        confirmed: false,
        dispatcher_id: dispatcherId,
        dispatcher_notes: notes || 'Request cancelled',
      });
    }
  };

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading request details...</p>
      </div>
    );
  }

  if (!request) {
    return (
      <div className="error-container">
        <AlertCircle size={48} />
        <h3>Request not found</h3>
        <button className="btn btn-primary" onClick={() => navigate('/')}>
          Back to Dashboard
        </button>
      </div>
    );
  }

  const extracted = request.extracted_info;
  const urgencyFactors = extracted?.urgency_factors;

  return (
    <div className="request-details-page">
      {/* Header */}
      <div className="details-header">
        <div>
          <h2>Emergency Request Details</h2>
          <p className="request-id">Request ID: {request.request_id}</p>
        </div>
        <div className="header-badges">
          <span className={`urgency-badge urgency-${extracted?.urgency_level}`}>
            {extracted?.urgency_level?.toUpperCase()}
          </span>
          <span className={`status-badge status-${request.status}`}>
            {request.status}
          </span>
        </div>
      </div>

      <div className="details-grid">
        {/* Left Column - Original Message & Extracted Info */}
        <div className="left-column">
          {/* Original Message */}
          <div className="detail-card">
            <h3>
              <FileText size={20} />
              Original Message
            </h3>
            <div className="message-box">
              <p>{request.original_message}</p>
            </div>
            <div className="message-meta">
              <div className="meta-item">
                <Clock size={14} />
                <span>
                  Received: {new Date(request.received_at).toLocaleString()}
                </span>
              </div>
              <div className="meta-item">
                <span>Source: {request.source}</span>
              </div>
              {request.phone_number && (
                <div className="meta-item">
                  <span>Phone: {request.phone_number}</span>
                </div>
              )}
            </div>
          </div>

          {/* Extracted Needs */}
          <div className="detail-card">
            <h3>Identified Needs</h3>
            <div className="needs-list">
              {extracted?.needs?.map((need, idx) => (
                <div key={idx} className="need-item">
                  <div className="need-header">
                    <span className="need-type">{need.need_type.replace('_', ' ')}</span>
                    <span className="confidence-badge">
                      {(need.confidence * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                  <p className="need-description">{need.description}</p>
                  {need.quantity && (
                    <p className="need-quantity">Quantity: {need.quantity}</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Location */}
          {extracted?.location && (
            <div className="detail-card">
              <h3>
                <MapPin size={20} />
                Location
              </h3>
              <div className="location-info">
                <p><strong>Raw Text:</strong> {extracted.location.raw_text}</p>
                {extracted.location.address && (
                  <p><strong>Address:</strong> {extracted.location.address}</p>
                )}
                {extracted.location.is_geocoded ? (
                  <p className="geocoded-success">
                    <CheckCircle size={14} />
                    Successfully geocoded
                  </p>
                ) : (
                  <p className="geocoded-warning">
                    <AlertCircle size={14} />
                    Could not geocode - distances may be inaccurate
                  </p>
                )}
              </div>
            </div>
          )}

          {/* People Affected & Vulnerable Populations */}
          <div className="detail-card">
            <h3>
              <Users size={20} />
              People Affected
            </h3>
            <div className="people-info">
              {extracted?.people_affected ? (
                <p className="people-count">
                  <strong>{extracted.people_affected}</strong> people affected
                </p>
              ) : (
                <p>Number of people unknown</p>
              )}

              {extracted?.vulnerable_populations?.length > 0 && (
                <div className="vulnerable-section">
                  <h4>Vulnerable Populations:</h4>
                  <div className="vulnerable-list">
                    {extracted.vulnerable_populations.map((vp, idx) => (
                      <div key={idx} className="vulnerable-item">
                        <span className="vulnerable-type">{vp.type}</span>
                        {vp.count && <span>({vp.count})</span>}
                        <p className="vulnerable-quote">"{vp.mentioned_in_text}"</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Urgency Scoring Explanation */}
          <div className="detail-card urgency-explanation">
            <h3>
              <TrendingUp size={20} />
              Urgency Analysis
            </h3>
            <div className="urgency-score-main">
              <div className="score-circle">
                <span className="score-value">
                  {((extracted?.urgency_score || 0) * 100).toFixed(0)}
                </span>
                <span className="score-label">Score</span>
              </div>
              <div>
                <h4>{extracted?.urgency_level?.toUpperCase()}</h4>
                <p>{extracted?.overall_explanation}</p>
              </div>
            </div>

            {urgencyFactors && (
              <div className="urgency-factors">
                <h4>Scoring Breakdown:</h4>
                
                <div className="factor">
                  <div className="factor-header">
                    <span>Medical Risk</span>
                    <span className="factor-score">
                      {(urgencyFactors.medical_risk_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="factor-bar">
                    <div
                      className="factor-fill"
                      style={{ width: `${urgencyFactors.medical_risk_score * 100}%` }}
                    />
                  </div>
                  <p className="factor-explanation">{urgencyFactors.medical_risk_explanation}</p>
                </div>

                <div className="factor">
                  <div className="factor-header">
                    <span>Vulnerable Populations</span>
                    <span className="factor-score">
                      {(urgencyFactors.vulnerable_pop_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="factor-bar">
                    <div
                      className="factor-fill"
                      style={{ width: `${urgencyFactors.vulnerable_pop_score * 100}%` }}
                    />
                  </div>
                  <p className="factor-explanation">{urgencyFactors.vulnerable_pop_explanation}</p>
                </div>

                <div className="factor">
                  <div className="factor-header">
                    <span>Time Sensitivity</span>
                    <span className="factor-score">
                      {(urgencyFactors.time_sensitivity_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="factor-bar">
                    <div
                      className="factor-fill"
                      style={{ width: `${urgencyFactors.time_sensitivity_score * 100}%` }}
                    />
                  </div>
                  <p className="factor-explanation">{urgencyFactors.time_sensitivity_explanation}</p>
                </div>

                <div className="factor">
                  <div className="factor-header">
                    <span>Message Confidence</span>
                    <span className="factor-score">
                      {(urgencyFactors.message_confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="factor-bar">
                    <div
                      className="factor-fill"
                      style={{ width: `${urgencyFactors.message_confidence_score * 100}%` }}
                    />
                  </div>
                  <p className="factor-explanation">{urgencyFactors.message_confidence_explanation}</p>
                </div>

                <div className="factor">
                  <div className="factor-header">
                    <span>Severity</span>
                    <span className="factor-score">
                      {(urgencyFactors.severity_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="factor-bar">
                    <div
                      className="factor-fill"
                      style={{ width: `${urgencyFactors.severity_score * 100}%` }}
                    />
                  </div>
                  <p className="factor-explanation">{urgencyFactors.severity_explanation}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column - Resource Matching & Actions */}
        <div className="right-column">
          {/* Matched Resources */}
          <div className="detail-card">
            <h3>
              <Navigation size={20} />
              Recommended Resources
            </h3>

            {request.matched_resources && request.matched_resources.length > 0 ? (
              <div className="resources-list">
                {request.matched_resources.map((match, idx) => (
                  <div
                    key={match.resource_id}
                    className={`resource-card ${selectedResourceId === match.resource_id ? 'selected' : ''}`}
                    onClick={() => setSelectedResourceId(match.resource_id)}
                  >
                    <div className="resource-header">
                      <div>
                        <h4>{match.resource_name}</h4>
                        <span className="resource-type">{match.resource_type}</span>
                      </div>
                      <div className="match-score">
                        {(match.match_score * 100).toFixed(0)}%
                      </div>
                    </div>

                    <p className="match-explanation">{match.overall_explanation}</p>

                    {match.distance_km && (
                      <div className="resource-meta">
                        <span>{match.distance_km.toFixed(1)} km away</span>
                        {match.estimated_arrival_minutes && (
                          <span>~{match.estimated_arrival_minutes} min ETA</span>
                        )}
                      </div>
                    )}

                    {match.trade_offs && match.trade_offs.length > 0 && (
                      <div className="trade-offs">
                        <strong>Trade-offs:</strong>
                        <ul>
                          {match.trade_offs.map((tradeoff, i) => (
                            <li key={i}>{tradeoff}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {idx === 0 && <div className="recommended-badge">RECOMMENDED</div>}
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-matches">No resource matches found</p>
            )}
          </div>

          {/* Dispatcher Actions */}
          {request.status === 'pending' && (
            <div className="detail-card actions-card">
              <h3>Dispatcher Actions</h3>
              
              <div className="form-group">
                <label htmlFor="notes">Notes</label>
                <textarea
                  id="notes"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add any notes about this dispatch decision..."
                  rows={4}
                />
              </div>

              <div className="action-buttons">
                <button
                  className="btn btn-success"
                  onClick={handleConfirm}
                  disabled={!selectedResourceId || confirmMutation.isPending}
                >
                  <CheckCircle size={20} />
                  Confirm Dispatch
                </button>
                <button
                  className="btn btn-danger"
                  onClick={handleCancel}
                  disabled={confirmMutation.isPending}
                >
                  <XCircle size={20} />
                  Cancel Request
                </button>
              </div>

              {!selectedResourceId && (
                <p className="warning-text">
                  <AlertCircle size={14} />
                  Please select a resource before confirming
                </p>
              )}
            </div>
          )}

          {/* Processing Stats */}
          {request.processing_time_seconds && (
            <div className="detail-card stats-card">
              <h3>Processing Statistics</h3>
              <div className="stat-row">
                <span>Processing Time:</span>
                <strong>{request.processing_time_seconds.toFixed(2)}s</strong>
              </div>
              <div className="stat-row">
                <span>Extraction Confidence:</span>
                <strong>{((extracted?.extraction_confidence || 0) * 100).toFixed(0)}%</strong>
              </div>
              {request.dispatched_at && (
                <div className="stat-row">
                  <span>Dispatched:</span>
                  <strong>{new Date(request.dispatched_at).toLocaleString()}</strong>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RequestDetailsPage;
