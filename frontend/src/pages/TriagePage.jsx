import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Send, AlertCircle, Loader } from 'lucide-react';
import { triageAPI } from '../services/api';
import './TriagePage.css';

const TriagePage = () => {
  const [message, setMessage] = useState('');
  const [source, setSource] = useState('sms');
  const [phoneNumber, setPhoneNumber] = useState('');
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // 🔵 DEMO FALLBACK DATA
  const demoResponse = {
    request_id: `demo-${Date.now()}`,
    urgency_level: 'CRITICAL',
    urgency_score: 92,
    explanation: [
      'High-risk emergency language detected',
      'Potential life-threatening situation',
      'Vulnerable individuals may be involved',
      'Immediate response required'
    ],
    extracted_info: {
      need: 'Emergency medical / rescue assistance',
      people_affected: 'Multiple',
      location: 'Location inferred from message'
    },
    recommended_resources: [
      'Nearest ambulance service',
      'Emergency hospital within 5 km',
      'Local disaster response NGO'
    ],
    demo_mode: true
  };

  const triageMutation = useMutation({
    mutationFn: async (payload) => {
      try {
        // Try real backend
        return await triageAPI.processMessage(payload);
      } catch (error) {
        // 🟢 FALLBACK TO DEMO MODE
        return demoResponse;
      }
    },
    onSuccess: (data) => {
      // Save to localStorage (session triage log)
      const history = JSON.parse(localStorage.getItem('triages')) || [];
      const entry = {
        timestamp: new Date().toLocaleString(),
        data
      };
      localStorage.setItem(
        'triages',
        JSON.stringify([entry, ...history])
      );

      queryClient.invalidateQueries(['requests']);
      navigate(`/requests/${data.request_id}`);
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!message.trim()) {
      alert('Please enter an emergency message');
      return;
    }

    triageMutation.mutate({
      message: message.trim(),
      source,
      phone_number: phoneNumber || null,
      timestamp: new Date().toISOString(),
      metadata: {}
    });
  };

  const exampleMessages = [
    {
      text: "Help! Building collapse at 123 Main St. Multiple people trapped. Children and elderly present. Need rescue team urgently!",
      category: "Critical Rescue"
    },
    {
      text: "Flood in downtown area near Central Park. About 50 families need evacuation. Water rising fast. Some elderly cannot move.",
      category: "Evacuation"
    },
    {
      text: "Medical emergency at Oak Street shelter. Woman in labor, no access to hospital. Need medical team immediately.",
      category: "Medical"
    },
    {
      text: "Over 100 people at Community Center with no food or water for 2 days. Children are crying. Please send supplies.",
      category: "Supplies"
    }
  ];

  return (
    <div className="triage-page">
      <div className="page-header">
        <div className="header-icon-wrapper">
          <AlertCircle size={32} />
        </div>
        <div>
          <h2>Emergency Message Triage</h2>
          <p className="page-description">
            AI-assisted, explainable emergency decision support
          </p>
        </div>
      </div>

      <div className="triage-grid">
        <div className="triage-form-container">
          <form onSubmit={handleSubmit} className="triage-form">
            <div className="form-group">
              <label>Emergency Message *</label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={12}
                disabled={triageMutation.isPending}
              />
              <div className="char-count">{message.length} characters</div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Message Source</label>
                <select
                  value={source}
                  onChange={(e) => setSource(e.target.value)}
                  disabled={triageMutation.isPending}
                >
                  <option value="sms">SMS</option>
                  <option value="social_media">Social Media</option>
                  <option value="chat">Chat</option>
                  <option value="phone">Phone</option>
                  <option value="email">Email</option>
                </select>
              </div>

              <div className="form-group">
                <label>Phone Number (Optional)</label>
                <input
                  type="tel"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  disabled={triageMutation.isPending}
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary submit-btn"
              disabled={triageMutation.isPending || !message.trim()}
            >
              {triageMutation.isPending ? (
                <>
                  <Loader className="spinner-icon" size={20} />
                  Processing...
                </>
              ) : (
                <>
                  <Send size={20} />
                  Process Emergency Request
                </>
              )}
            </button>

            <small style={{ opacity: 0.6, marginTop: '8px', display: 'block' }}>
              Demo mode enabled – backend integration simulated if unavailable
            </small>
          </form>
        </div>

        <div className="examples-container">
          <h3>Example Emergency Messages</h3>
          <div className="examples-list">
            {exampleMessages.map((ex, i) => (
              <div
                key={i}
                className="example-card"
                onClick={() => setMessage(ex.text)}
              >
                <div className="example-category">{ex.category}</div>
                <div className="example-text">{ex.text}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TriagePage;
