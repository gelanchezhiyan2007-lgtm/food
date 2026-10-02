# ⚖️ LegalEase: AI-Powered Legal Document Generator

LegalEase is a full-stack legal technology platform powered by **FastAPI**, **SQLite Database**, **Streamlit**, and **Google Gemini 1.5 Pro**. It enables users to generate, edit, preview, and download customized, professional legal agreements in `.DOCX`, `.PDF`, and `.TXT` formats.

---

## 📂 Project Structure

```
legalease/
├── app.py                  # Streamlit Frontend UI Studio
├── main.py                 # FastAPI Backend Entry Point
├── routes.py               # API Route Handlers & Pydantic Schemas
├── database.py             # SQLite Database Manager (legalease.db)
├── requirements.txt        # Python Dependencies
├── Dockerfile              # Container Deployment Configuration
├── Procfile                # Render / Railway Deployment Script
├── .env                    # Environment Variable Template
├── test_legal_ease.py      # Automated Test Suite
├── ai_core/
│   └── gemini_generator.py # Gemini 1.5 Pro AI Engine Core
├── utils/
│   ├── formatters.py       # DOCX, PDF, and HTML Card Generators
│   └── text_sanitizer.py   # Text Sanitization & Unicode Cleaning
└── assets/
    └── legalease_logo.png  # Brand Logo Asset
```

---

## 🚀 How to Run Locally

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Key** in `.env`:
   ```env
   GEMINI_API_KEY=your_google_gemini_api_key
   ```

3. **Start FastAPI Backend Server**:
   ```bash
   python -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```

4. **Launch Streamlit Frontend**:
   ```bash
   streamlit run app.py --server.port 8501
   ```

---

## ☁️ Deployment Instructions (Hosting Options)

### Option 1: Deploy on Render / Railway
1. Push this folder to a GitHub Repository.
2. Create a **Web Service** on [Render](https://render.com) or [Railway](https://railway.app).
3. Set the environment variable: `GEMINI_API_KEY`.
4. Render will automatically detect the `Procfile` and deploy both FastAPI and Streamlit!

### Option 2: Deploy using Docker
Build and run the Docker container:
```bash
docker build -t legalease .
docker run -p 8000:8000 -p 8501:8501 -e GEMINI_API_KEY="your_api_key" legalease
```

### Option 3: Deploy Frontend on Streamlit Community Cloud
1. Deploy `app.py` to [Streamlit Community Cloud](https://streamlit.io/cloud).
2. Deploy `main.py` on Render, Fly.io, or any VPS.
3. Set `BACKEND_URL` environment variable in Streamlit secrets pointing to your live FastAPI backend URL.
