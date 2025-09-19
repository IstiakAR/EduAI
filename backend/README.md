# EduAI - Simple Backend

A minimal FastAPI backend that allows clients to send questions to Google's Gemini AI and receive responses.

## Features

- Simple FastAPI server with CORS support
- Direct integration with Google Gemini AI
- Single endpoint for chat functionality
- Health check endpoint
- No database or authentication required

## Setup

1. Install dependencies:
```bash
pip install -r requirements_simple.txt
```

2. Set up environment variables in `.env`:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

3. Run the server:
```bash
python main.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/health`
- Returns server status and AI availability

### Chat
- **POST** `/chat`
- Send a question to Gemini AI
- Request body: `{"message": "Your question here"}`
- Response: `{"response": "AI response", "success": true}`

## Example Usage

```bash
# Health check
curl http://localhost:8000/health

# Send a question
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is machine learning?"}'
```

## File Structure

```
backend/
├── main.py                    # Main FastAPI application
├── requirements_simple.txt    # Minimal dependencies
├── .env                      # Environment variables
└── backup_complex/           # Backup of complex files
```

The `backup_complex/` directory contains the more complex authentication, database, and service files that were removed to simplify the backend.