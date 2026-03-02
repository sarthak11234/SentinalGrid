<p align="center">
  <h1 align="center">🟢 SentinalGrid</h1>
  <p align="center">
    <strong>Agentic Spreadsheet & Communication Platform</strong>
  </p>
  <p align="center">
    Upload a spreadsheet. Write a prompt. Let AI draft personalized messages and manage replies — automatically.
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white" alt="Python 3.10+">
    <img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white" alt="FastAPI">
    <img src="https://img.shields.io/badge/Gemini-AI-4285F4?logo=googlegemini&logoColor=white" alt="Gemini AI">
    <img src="https://img.shields.io/badge/WhatsApp-25D366?logo=whatsapp&logoColor=white" alt="WhatsApp">
    <img src="https://img.shields.io/badge/License-MIT-yellow" alt="MIT License">
  </p>
</p>

---

## 📌 Overview

**SentinalGrid** is an AI-powered communication platform that turns your spreadsheet data into personalized outbound campaigns over **WhatsApp** and **Email**. Powered by **Google Gemini**, it reads each row of your uploaded data, drafts a unique message per recipient, sends it through the appropriate channel, and intelligently processes inbound replies — updating your dataset automatically.

When the AI is uncertain about a reply, it flags the row for **human review**, ensuring data integrity with a confidence-based approval workflow.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 📤 **Multi-Channel Outreach** | Send personalized messages via **WhatsApp** (WAHA) and **Email** (Gmail SMTP) |
| 🤖 **AI-Drafted Messages** | Google Gemini drafts unique messages per row based on a master prompt |
| 📥 **Smart Reply Processing** | Inbound replies are analyzed by AI to extract intent and data updates |
| ⚖️ **Confidence Scoring** | Low-confidence replies are flagged for human review instead of auto-updating |
| 📊 **Campaign Dashboard** | Real-time stats — pending, sent, replied, and flagged rows at a glance |
| 🔄 **Webhook Integration** | WAHA WhatsApp webhook for real-time inbound message processing |
| 🔐 **Google OAuth** | Secure authentication via Google SSO |
| 🧠 **Model Selection** | Switch between Gemini models (2.5 Pro, 2.5 Flash, 2.0 Flash) on the fly |
| 🌗 **Dark / Light Mode** | Sleek UI with theme toggle |

---

## 🏗️ Architecture

```
┌─────────────────┐       ┌──────────────────────────────────────┐
│   Frontend UI   │◄─────►│         FastAPI Backend (8000)        │
│  (HTML/CSS/JS)  │       │                                      │
└─────────────────┘       │  ┌──────────┐  ┌──────────────────┐  │
                          │  │  Google   │  │   Messaging      │  │
                          │  │  Gemini   │  │  ┌────────────┐  │  │
                          │  │  (Agent)  │  │  │ WhatsApp   │  │  │
                          │  │          │  │  │  (WAHA)    │  │  │
                          │  └──────────┘  │  ├────────────┤  │  │
                          │                │  │ Email      │  │  │
                          │                │  │  (SMTP)    │  │  │
                          │                │  └────────────┘  │  │
                          │  ┌──────────────────────────────┐  │  │
                          │  │    SQLite + SQLAlchemy ORM   │  │  │
                          │  └──────────────────────────────┘  │  │
                          └──────────────────────────────────────┘
                                        ▲
                                        │ Webhooks
                          ┌─────────────┴─────────────┐
                          │   WAHA (WhatsApp Gateway)  │
                          │     Docker — port 3000     │
                          └───────────────────────────┘
```

### How It Works

1. **Upload & Configure** — Upload a CSV/XLSX file and write a master prompt describing what to communicate.
2. **AI Drafts Messages** — Gemini reads each row and drafts a personalized message.
3. **Multi-Channel Send** — Messages are dispatched via WhatsApp or Email based on available contact info.
4. **Receive Replies** — WAHA webhooks forward inbound WhatsApp replies to the backend.
5. **AI Processes Replies** — The agent extracts intent and suggested data updates from each reply.
6. **Human-in-the-Loop** — Low-confidence extractions are flagged for manual review in the Review Queue.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python · FastAPI · Uvicorn |
| **AI / LLM** | Google Gemini (via LangChain) |
| **Database** | SQLite · SQLAlchemy ORM |
| **WhatsApp** | WAHA (self-hosted WhatsApp HTTP API) |
| **Email** | aiosmtplib (Gmail SMTP) |
| **Auth** | Google OAuth 2.0 (custom HMAC tokens) |
| **Frontend** | Vanilla HTML · CSS · JavaScript |
| **Data Processing** | Pandas |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Docker** (for WAHA WhatsApp gateway)
- A **Google Cloud** project with OAuth 2.0 credentials
- A **Gemini API key** ([Get one free](https://aistudio.google.com/apikey))
- A **Gmail App Password** (for SMTP email sending)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/SentinalGrid.git
cd SentinalGrid
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Google Gemini (free tier)
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash

# Email / SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# WAHA WhatsApp (self-hosted)
WAHA_URL=http://localhost:3000
WAHA_API_KEY=mykey123
WAHA_SESSION=default

# Database
DATABASE_URL=sqlite:///./data/sentinalgrid.db

# App
SECRET_KEY=change-me-to-a-random-string
FRONTEND_URL=http://localhost:8501
CONFIDENCE_THRESHOLD=0.7
```

### 5. Start WAHA (WhatsApp Gateway)

```bash
docker run -d \
  --name waha \
  -p 3000:3000 \
  -e WHATSAPP_DEFAULT_ENGINE=WEBJS \
  -e WAHA_API_KEY_PLAIN=mykey123 \
  devlikeapro/waha
```

> After starting, scan the QR code at `http://localhost:3000` to link your WhatsApp account.

### 6. Start the Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000` with interactive docs at `/docs`.

### 7. Start the Frontend

Open `frontend/index.html` directly in your browser, or serve it with any static file server:

```bash
# Quick option with Python
cd frontend
python -m http.server 8501
```

---

## 📡 API Reference

Base URL: `http://localhost:8000`

### System

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/auth/login` | Redirect to Google OAuth consent screen |
| `GET` | `/auth/callback` | OAuth callback — exchanges code for session token |

### Campaigns

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/campaigns` | Create a new campaign (multipart form + file upload) |
| `GET` | `/campaigns` | List all campaigns |
| `GET` | `/campaigns/{id}` | Get campaign details with rows and stats |
| `POST` | `/campaigns/{id}/launch` | Launch a campaign (drafts & sends messages in background) |
| `GET` | `/campaigns/{id}/reviews` | Get rows flagged for human review |
| `POST` | `/campaigns/{id}/rows/{row_id}/review` | Approve or reject a suggested update |

### Webhooks

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/webhooks/whatsapp` | WAHA inbound message webhook |
| `POST` | `/webhooks/manual-reply` | Manual reply input (prototype) |
| `POST` | `/webhooks/send-whatsapp` | Quick one-off WhatsApp message |
| `GET` | `/webhooks/whatsapp-status` | Check WAHA connection status |
| `POST` | `/webhooks/email` | Email inbound webhook (placeholder) |

### Settings

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/settings/models` | Get current and available Gemini models |
| `POST` | `/settings/models` | Switch the active Gemini model |

---

## 📂 Project Structure

```
SentinalGrid/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app entry point & CORS config
│   │   ├── config.py         # Pydantic Settings (env vars)
│   │   ├── database.py       # SQLAlchemy engine & session setup
│   │   ├── models.py         # ORM models — Campaign, DataRow
│   │   ├── schemas.py        # Pydantic request/response schemas
│   │   ├── agent.py          # Gemini AI — message drafting & reply processing
│   │   ├── auth.py           # Google OAuth 2.0 login flow
│   │   ├── messaging.py      # Email (SMTP) + WhatsApp (WAHA) senders
│   │   └── routers/
│   │       ├── campaigns.py  # Campaign CRUD, file upload & launch
│   │       ├── webhooks.py   # Inbound reply webhooks (WhatsApp, Email)
│   │       └── settings.py   # Model selection API
│   └── requirements.txt
├── frontend/
│   ├── index.html            # Single-page app (sidebar nav, 3 pages)
│   ├── style.css             # Full styling with dark/light themes
│   └── script.js             # API client & UI logic
├── docs/
│   └── architecture_proposal.md
├── .env.example              # Environment variable template
├── .gitignore
├── requirements.txt          # Top-level dependency list
└── README.md
```

---

## 🔧 Configuration

| Variable | Description | Default |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API key | — |
| `GEMINI_MODEL` | Active Gemini model | `gemini-2.5-flash` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | — |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | — |
| `SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USER` | SMTP sender email | — |
| `SMTP_PASS` | SMTP app password | — |
| `WAHA_URL` | WAHA API base URL | `http://localhost:3000` |
| `WAHA_API_KEY` | WAHA API key | — |
| `WAHA_SESSION` | WAHA session name | `default` |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///./data/sentinalgrid.db` |
| `SECRET_KEY` | Secret for signing auth tokens | — |
| `FRONTEND_URL` | Frontend URL (for CORS & OAuth redirect) | `http://localhost:8501` |
| `CONFIDENCE_THRESHOLD` | Min confidence for auto-updating rows | `0.7` |

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** this repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ using FastAPI, Google Gemini & WAHA
</p>
