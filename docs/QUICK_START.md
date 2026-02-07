# Quick Start Guide

## Emergency Crisis Triage System - Quick Setup

### 1. Install MongoDB

**Windows:**
```powershell
# Download and install MongoDB Community Server from:
# https://www.mongodb.com/try/download/community

# Or use with Chocolatey:
choco install mongodb

# Start MongoDB:
net start MongoDB
```

**Mac (with Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Or use MongoDB Atlas (Cloud):**
- Sign up at https://www.mongodb.com/cloud/atlas
- Create free cluster
- Get connection string
- Update `MONGODB_URL` in `.env`

### 2. Get API Keys

**OpenAI (Recommended):**
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Copy the key

**Anthropic (Alternative):**
1. Go to https://console.anthropic.com/
2. Create API key
3. Copy the key

### 3. Backend Setup (5 minutes)

```bash
# Navigate to project
cd emergency-crisis-triage/backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
copy .env.example .env

# Edit .env and add your API key:
# OPENAI_API_KEY=sk-your-key-here

# Load sample data
python scripts/load_sample_data.py

# Start server
python -m uvicorn app.main:app --reload

# ✓ Backend running at http://localhost:8000
# ✓ API docs at http://localhost:8000/docs
```

### 4. Frontend Setup (3 minutes)

```bash
# Open new terminal
cd emergency-crisis-triage/frontend

# Install dependencies
npm install

# Start development server
npm run dev

# ✓ Frontend running at http://localhost:3000
```

### 5. Test the System

1. **Open browser:** http://localhost:3000

2. **Go to "New Triage" page**

3. **Try an example message:**
   ```
   Help! Building collapse at 123 Main St. 
   Multiple people trapped. Children and elderly present. 
   Need rescue team urgently!
   ```

4. **Click "Process Emergency Request"**

5. **Review the AI analysis:**
   - Extracted needs
   - Urgency classification with explanation
   - Matched resources
   - Trade-off analysis

6. **Select a resource and confirm dispatch**

## Common Issues

### MongoDB Connection Failed
```bash
# Check if MongoDB is running:
mongosh

# If not, start it:
# Windows:
net start MongoDB

# Mac:
brew services start mongodb-community
```

### API Key Error
- Make sure `.env` file exists in `backend/` directory
- Verify API key is correctly pasted (no extra spaces)
- Check key has proper permissions on API provider dashboard

### Port Already in Use
```bash
# Backend (port 8000):
python -m uvicorn app.main:app --reload --port 8001

# Frontend (port 3000):
npm run dev -- --port 3001
```

### Dependencies Installation Failed
```bash
# Clear cache and retry:
pip cache purge
pip install -r requirements.txt

# For frontend:
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

- [ ] Review dashboard metrics at http://localhost:3000
- [ ] Test API endpoints at http://localhost:8000/docs
- [ ] Try different example messages
- [ ] Check resource management page
- [ ] Review request details and explanations
- [ ] Test dispatcher confirmation workflow

## Production Deployment

See `docs/DEPLOYMENT.md` for production deployment guide.

## Support

- API Documentation: http://localhost:8000/docs
- Check logs in terminal windows
- Review README.md for detailed documentation
