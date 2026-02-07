# Emergency Crisis Triage & Resource Allocation System

## Overview

An AI-powered decision support system designed to assist emergency response coordinators and NGO dispatchers operating under extreme time pressure. The system analyzes unstructured crisis messages and provides faster, safer, and more transparent emergency triage and resource allocation.

### 🎯 Primary Objective

**Reduce emergency request triage time by at least 40%** while maintaining:
- Human-in-the-loop control
- Safety and fairness
- Transparency and explainability
- Auditability

## ✨ Key Features

### 1. **Intelligent Message Processing**
- Accepts unstructured crisis messages from SMS, social media, chat platforms
- Handles incomplete, emotional, multilingual, or ambiguous messages
- Extracts structured information using advanced LLM technology

### 2. **Explainable Urgency Scoring**
- Transparent urgency classification (Critical, High, Medium, Low)
- Detailed breakdown of scoring factors:
  - Medical risk assessment
  - Vulnerable population identification
  - Time sensitivity analysis
  - Message confidence evaluation
  - Severity indicators
- **Every score includes a clear explanation** of the reasoning

### 3. **Smart Resource Matching**
- Multi-factor matching algorithm considers:
  - **Suitability** (40%): Does the resource match the need?
  - **Availability** (30%): Is the resource currently available?
  - **Capacity** (15%): Can it handle the number of people?
  - **Distance** (15%): How close is the resource?
- Provides trade-off analysis for informed decisions
- Calculates estimated arrival times

### 4. **Human-in-the-Loop Design**
- Dispatchers maintain final decision authority
- High-risk decisions require explicit human confirmation
- System tracks human overrides for continuous improvement
- Clear confidence levels displayed throughout

### 5. **Real-Time Dashboard**
- Monitor pending and active requests
- Track resource availability
- View performance metrics
- Detailed request analysis with full explanations

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **FastAPI** REST API
- **MongoDB** for data persistence
- **OpenAI/Anthropic** LLM integration for NLP
- **Beanie ODM** for document modeling
- Modular service architecture

### Frontend (React)
- **React 18** with modern hooks
- **TanStack Query** for data management
- **Lucide React** icons
- Responsive design for desktop and mobile

## 📦 Installation & Setup

### Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **MongoDB 6.0+** (local or cloud)
- **OpenAI API Key** or **Anthropic API Key**

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment:**
   ```bash
   copy .env.example .env
   ```
   Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_key_here
   # OR
   ANTHROPIC_API_KEY=your_anthropic_key_here
   
   MONGODB_URL=mongodb://localhost:27017
   ```

6. **Start MongoDB:**
   - Ensure MongoDB is running on `mongodb://localhost:27017`
   - Or use MongoDB Atlas (cloud) and update the URL in `.env`

7. **Run the backend:**
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

   Backend will be available at: `http://localhost:8000`
   API Documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

   Frontend will be available at: `http://localhost:3000`

### Load Sample Data (Optional)

```bash
cd backend
python scripts/load_sample_data.py
```

## 🚀 Usage

### 1. Process Emergency Message

The system can process unstructured messages like:

> "Help! Building collapse at 123 Main St. Multiple people trapped. Children and elderly present. Need rescue team urgently!"

**Via Dashboard:**
1. Go to "New Triage" page
2. Enter or paste the emergency message
3. Select message source (SMS, social media, etc.)
4. Click "Process Emergency Request"

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/v1/triage" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Medical emergency at Oak Street shelter. Woman in labor, no access to hospital.",
    "source": "sms",
    "timestamp": "2026-02-07T10:30:00Z"
  }'
```

### 2. Review AI Analysis

The system provides:
- **Extracted needs** with confidence scores
- **Location information** (geocoded when possible)
- **Urgency score** with detailed explanation
- **Matched resources** ranked by suitability
- **Trade-off analysis** for decision support

### 3. Confirm Dispatch

Dispatcher reviews recommendations and:
- Selects a resource (can override AI recommendation)
- Adds notes
- Confirms dispatch

All decisions are logged for accountability and continuous learning.

## 📊 Key Metrics

The system tracks:
- **Average triage time** (target: 40% reduction)
- **Request distribution** by urgency
- **Resource utilization**
- **Human override rate**
- **Response times**

## 🔒 Safety & Ethics

### Human-in-the-Loop Safeguards

✅ **Dispatchers always make the final decision**  
✅ High-impact actions require explicit human confirmation  
✅ Display confidence levels and uncertainty  
✅ Allow human overrides and feedback loops

### Risk Mitigation

⚠️ **Potential Harm:** Incorrect urgency classification could delay assistance to critical cases

**Mitigations:**
- Maintain human-in-the-loop control
- Require dispatcher confirmation for high-risk actions
- Continuously surface explanations and uncertainty
- Track all decisions for audit

### Inclusion & Bias Awareness

The system is designed to:
- Handle unclear or fragmented language gracefully
- Avoid penalizing poor grammar or emotional expression
- Work with multilingual messages
- Consider accessibility for elderly and low-literacy populations

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
pytest tests/
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Process test message
curl -X POST http://localhost:8000/api/v1/triage \
  -H "Content-Type: application/json" \
  -d @tests/sample_message.json
```

## 📂 Project Structure

```
emergency-crisis-triage/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── models/       # Data models & schemas
│   │   ├── services/     # Business logic
│   │   │   ├── nlp_service.py          # NLP extraction
│   │   │   ├── resource_matching.py    # Resource matching
│   │   │   ├── triage_service.py       # Main triage orchestration
│   │   │   └── geocoding.py            # Location services
│   │   ├── config.py     # Configuration
│   │   ├── database.py   # DB connection
│   │   └── main.py       # FastAPI app
│   ├── tests/            # Unit tests
│   ├── requirements.txt  # Python dependencies
│   └── .env.example      # Environment template
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API client
│   │   └── main.jsx      # App entry point
│   ├── package.json      # Node dependencies
│   └── vite.config.js    # Vite configuration
├── data/                 # Sample data
├── docs/                 # Additional documentation
└── README.md            # This file
```

## 🔧 Configuration

### Urgency Scoring Weights (configurable)
- Medical Risk: 35%
- Vulnerable Populations: 25%
- Time Sensitivity: 20%
- Message Confidence: 10%
- Severity: 10%

### Resource Matching Weights (configurable)
- Suitability: 40%
- Availability: 30%
- Capacity: 15%
- Distance: 15%

Edit these in `backend/.env` or `backend/app/config.py`

## 🤝 Contributing

This is a mission-critical system. Contributions must:
1. Maintain human-in-the-loop controls
2. Include comprehensive tests
3. Document decision-making logic
4. Consider safety implications
5. Preserve explainability

## 📝 License

[Add your license here]

## 🆘 Support

For issues or questions:
- Check the API documentation at `/docs`
- Review logs in the backend console
- Ensure MongoDB is running
- Verify API keys are correctly configured

## ⚠️ Important Notes

### Production Deployment

Before deploying to production:

1. **Security:**
   - Change `SECRET_KEY` in `.env`
   - Use HTTPS for all connections
   - Implement proper authentication
   - Configure CORS appropriately

2. **Scalability:**
   - Use production MongoDB (e.g., MongoDB Atlas)
   - Configure proper connection pooling
   - Implement rate limiting
   - Add caching layer

3. **Monitoring:**
   - Set up error tracking (e.g., Sentry)
   - Configure logging aggregation
   - Monitor API response times
   - Track system performance metrics

4. **Compliance:**
   - Ensure HIPAA/GDPR compliance if applicable
   - Implement data retention policies
   - Configure audit logging
   - Document decision-making processes

## 🎯 Success Criteria

- [ ] ≥40% reduction in average emergency triage time
- [ ] Improved dispatcher trust and adoption
- [ ] Clear, auditable decision explanations
- [ ] Safer and more equitable resource allocation
- [ ] High accuracy in urgency classification
- [ ] Minimal human overrides required

---

**Remember:** This system is a **decision support tool**, not an autonomous decision-maker. Human judgment remains paramount in emergency response.
