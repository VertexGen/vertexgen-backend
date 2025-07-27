# VertexGen Backend

**VertexGen** is an intelligent backend orchestrator designed to empower farmers with AI-driven assistance. Built for hackathons, it leverages Google Vertex AI, Gemini, and multi-agent tools to deliver crop diagnosis, financial planning, inventory management, market analysis, government scheme navigation, and more.

---

## 🚀 Project Highlights

- **Crop Diagnosis:** Diagnose plant diseases using images and text queries.
- **Financial Planning:** Calculate costs, profits, and yields for crop farming.
- **Inventory Management:** Track farm stock, reorder supplies, and place orders.
- **Market Analysis:** Fetch mandi crop prices and provide market advice.
- **Government Schemes:** Discover and apply for relevant agricultural schemes.
- **Weather Advisory:** Get weather forecasts and actionable crop recommendations.
- **Audio & Translation Services:** Text-to-speech, translation, and audio transcription.

---

## 🛠️ Tech Stack

- **Python 3.9**
- **FastAPI** for REST APIs
- **Google Vertex AI & Gemini** for generative AI
- **Firebase** for audio storage
- **SQLAlchemy** with PostgreSQL for database
- **Docker** for containerization

---

## Architecture Diagram
![Architecture Diagram](file:///Users/timsal/Desktop/Screenshot%202025-07-27%20at%2012.25.01%E2%80%AFPM.png)

## ⚡ Quick Start

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/vertexgen-backend.git
cd vertexgen-backend
```

### 2. Install Dependencies

```sh
pip install -r requirements.txt
```

### 3. Configure Environment Variables

- Copy `.env.example` to `.env` and fill in your credentials.
- Example keys:
  - `FIREBASE_BUCKET`
  - `GOOGLE_APPLICATION_CREDENTIALS`
  - `VERTEX_PROJECT_ID`
  - `GEMINI_API_KEY`
  - `DATABASE_URL`

### 4. Run the API Server

```sh
uvicorn api.main:app --host 0.0.0.0 --port 8080
```

### 5. Docker (Optional)

```sh
docker build -t vertexgen-backend .
docker run -p 8080:8080 --env-file .env vertexgen-backend
```

---

## 📚 API Endpoints

| Endpoint                | Method | Description                                      |
|-------------------------|--------|--------------------------------------------------|
| `/ask`                  | POST   | Main orchestrator endpoint for farmer queries     |
| `/audio/generate`       | POST   | Generate audio from text                         |
| `/translate`            | POST   | Translate text to another language               |
| `/transcribe`           | POST   | Transcribe audio to text                         |

---

## 📁 Folder Structure

```
vertexgen-backend/
├── api/                # FastAPI endpoints
├── db/                 # Database models and setup
├── models/             # Pydantic models
├── multi_agent/        # Agent and tool implementations
├── service/            # Service modules (TTS, translation, transcription)
├── specs/              # Domain specs (submodule)
├── requirements.txt
├── Dockerfile
└── .env
```

---

## 👥 Team

- Timsal, Vridhi, Sparsh & Umesh

---

## 📝 License

MIT License

---

**Built for Hackathons. Empowering Farmers with AI.**
