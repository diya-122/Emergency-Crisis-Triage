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

  const triageMutation = useMutation({
    mutationFn: triageAPI.processMessage,
    onSuccess: (data) => {
      queryClient.invalidateQueries(['requests']);
      navigate(`/requests/${data.request_id}`);
    },
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
      metadata: {},
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

  const loadExample = (exampleText) => {
    setMessage(exampleText);
  };

  return (
    <div className="triage-page">
      <div className="page-header">
        <div className="header-icon-wrapper">
          <AlertCircle size={32} />
        </div>
        <div>
          <h2>Emergency Message Triage</h2>
          <p className="page-description">
            Process unstructured emergency messages with AI-assisted analysis
          </p>
        </div>
      </div>

      <div className="triage-grid">
        {/* Input Form */}
        <div className="triage-form-container">
          <form onSubmit={handleSubmit} className="triage-form">
            <div className="form-group">
              <label htmlFor="message">Emergency Message *</label>
              <textarea
                id="message"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Enter the unstructured emergency message here...&#10;&#10;The AI will extract and analyze:&#10;- What help is needed&#10;- Location information&#10;- Number of people affected&#10;- Urgency level&#10;- Vulnerable populations"
                rows={12}
                required
                disabled={triageMutation.isPending}
              />
              <div className="char-count">
                {message.length} characters
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="source">Message Source</label>
                <select
                  id="source"
                  value={source}
                  onChange={(e) => setSource(e.target.value)}
                  disabled={triageMutation.isPending}
                >
                  <option value="sms">SMS</option>
                  <option value="social_media">Social Media</option>
                  <option value="chat">Chat</option>
                  <option value="phone">Phone</option>
                  <option value="email">Email</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="phone">Phone Number (Optional)</label>
                <input
                  type="tel"
                  id="phone"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  placeholder="+1234567890"
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

            {triageMutation.isError && (
              <div className="error-message">
                <AlertCircle size={16} />
                Error processing message: {triageMutation.error.message}
              </div>
            )}
          </form>
        </div>

        {/* Examples Sidebar */}
        <div className="examples-container">
          <h3>Example Emergency Messages</h3>
          <p className="examples-description">
            Click an example to try the system:
          </p>

          <div className="examples-list">
            {exampleMessages.map((example, index) => (
              <div
                key={index}
                className="example-card"
                onClick={() => loadExample(example.text)}
              >
                <div className="example-category">{example.category}</div>
                <div className="example-text">{example.text}</div>
                <button type="button" className="example-load-btn">
                  Load Example
                </button>
              </div>
            ))}
          </div>

          <div className="info-box">
            <h4>How it works:</h4>
            <ol>
              <li>Enter or paste an emergency message</li>
              <li>AI extracts structured information</li>
              <li>Calculates explainable urgency score</li>
              <li>Matches to available resources</li>
              <li>Provides decision support for dispatcher</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TriagePage;
